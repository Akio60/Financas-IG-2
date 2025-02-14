/**
 * Gatilho de envio de formulário.
 * Preenche o ID (se estiver vazio) com valor único sequencial no formato "YYYY - 0001" etc.
 * Verifica duplicatas na coluna "Id".
 */

/**
 * Envia email de notificação para os responsáveis.
 * @param {Object} formData - Dados do formulário submetido
 */
function sendNotificationEmail(formData) {
  try {
    // Pega a aba Email
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var emailSheet = spreadsheet.getSheetByName('Email');
    if (!emailSheet) {
      Logger.log('Aba Email não encontrada');
      return;
    }

    // Pega os emails da coluna AguardandoAprovacao
    var headerRow = emailSheet.getRange(1, 1, 1, emailSheet.getLastColumn()).getValues()[0];
    var aguardandoIndex = headerRow.indexOf('AguardandoAprovacao') + 1;
    
    if (aguardandoIndex <= 0) {
      Logger.log('Coluna AguardandoAprovacao não encontrada');
      return;
    }

    // Pega os emails (assume que estão na primeira linha de dados, linha 2)
    var emailsCell = emailSheet.getRange(2, aguardandoIndex).getValue();
    if (!emailsCell) return;

    var emails = emailsCell.toString().split(',').map(e => e.trim()).filter(e => e);
    if (emails.length === 0) return;

    // Prepara o conteúdo do email
    var subject = '[Sistema Financeiro IG] Nova Solicitação - Aguardando Aprovação';
    var body = `Prezado(a) responsável,

Uma nova solicitação foi recebida e requer sua atenção.

=== DETALHES DA SOLICITAÇÃO ===
ID: ${formData.id}
Data: ${formData.timestamp}

=== DADOS DO SOLICITANTE ===
Nome: ${formData['Nome completo (sem abreviações):']}
CPF: ${formData['CPF:']}
Curso: ${formData['Curso:']}
Orientador: ${formData['Orientador']}

=== INFORMAÇÕES FINANCEIRAS ===
Valor Solicitado: R$ ${formData['Valor solicitado. Somente valor, sem pontos e vírgula']}
Motivo: ${formData['Motivo da solicitação']}

Para acessar mais detalhes ou tomar ações, por favor acesse o sistema.

Atenciosamente,
Sistema Financeiro IG-UNICAMP

--
Este é um email automático. Para questões específicas, entre em contato com a
Gestão Financeira do IG através do email gestao.financeira@ig.unicamp.br`;

    // Envia o email para cada destinatário
    emails.forEach(email => {
      MailApp.sendEmail({
        to: email,
        subject: subject,
        body: body
      });
      Logger.log(`Email enviado para ${email}`);
    });

  } catch (error) {
    Logger.log('Erro ao enviar email: ' + error.toString());
  }
}

/**
 * Função auxiliar para extrair dados do formulário
 */
function getFormData(e) {
  var sheet = e.range.getSheet();
  var row = e.range.getRow();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var values = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  var formData = {
    timestamp: new Date().toLocaleString(),
    id: values[headers.indexOf('Id')]
  };

  // Mapeia todos os campos do formulário
  headers.forEach((header, index) => {
    formData[header] = values[index];
  });

  return formData;
}

/**
 * Verifica as permissões necessárias para o funcionamento do script
 */
function checkPermissions() {
  try {
    // Testa acesso ao Gmail/Mail
    MailApp.getRemainingDailyQuota();
    
    // Testa acesso à planilha
    var sheet = SpreadsheetApp.getActiveSpreadsheet();
    sheet.getName();
    
    // Testa acesso às propriedades do script
    var scriptProperties = PropertiesService.getScriptProperties();
    var nextId = scriptProperties.getProperty("NEXT_ID");
    
    return {
      success: true,
      message: "Todas as permissões OK"
    };
  } catch (e) {
    return {
      success: false,
      message: "Erro de permissão: " + e.toString()
    };
  }
}

// Modifique onFormSubmit para verificar permissões
function onFormSubmit(e) {
  // Verifica permissões primeiro
  var permissions = checkPermissions();
  if (!permissions.success) {
    Logger.log("Erro de permissões: " + permissions.message);
    return;
  }

  var sheet = e.range.getSheet();
  var lastRow = e.range.getRow();

  // Gera e insere ID como antes
  var colId = findIdColumnIndex(sheet);
  if (colId <= 0) return;

  var currentID = sheet.getRange(lastRow, colId).getValue();
  if (currentID) return;

  var newId = generateUniqueId(sheet);
  sheet.getRange(lastRow, colId).setValue(newId);

  // Depois de gerar o ID, envia a notificação
  var formData = getFormData(e);
  sendNotificationEmail(formData);
}

function notifyNewSubmission(formResponse) {
  // Verifica permissões primeiro
  var permissions = checkPermissions();
  if (!permissions.success) {
    Logger.log("Erro de permissões para envio de email: " + permissions.message);
    return;
  }

  try {
    // Pega a aba Email
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var emailSheet = spreadsheet.getSheetByName('Email');
    if (!emailSheet) {
      Logger.log('Aba Email não encontrada');
      return;
    }

    // Pega os emails para AguardandoAprovacao
    var data = emailSheet.getDataRange().getValues();
    var headers = data[0];
    var aguardandoIndex = headers.indexOf('AguardandoAprovacao');
    if (aguardandoIndex === -1) {
      Logger.log('Coluna AguardandoAprovacao não encontrada');
      return;
    }

    // Pega os emails (primeira linha de dados após o header)
    var emailsStr = data[1][aguardandoIndex];
    if (!emailsStr) {
      Logger.log('Nenhum email configurado para AguardandoAprovacao');
      return;
    }

    var emails = emailsStr.split(',').map(e => e.trim()).filter(e => e);
    if (emails.length === 0) return;

    // Prepara o email
    var formData = formResponse.namedValues;
    var subject = '[Sistema Financeiro IG] Nova Solicitação';
    var body = `
      Uma nova solicitação foi recebida:
      
      Nome: ${formData['Nome completo (sem abreviações):'][0]}
      Curso: ${formData['Curso:'][0]}
      Motivo: ${formData['Motivo da solicitação'][0]}
      Valor Solicitado: R$ ${formData['Valor solicitado. Somente valor, sem pontos e vírgula'][0]}
      
      Por favor, acesse o sistema para mais detalhes.
      
      Atenciosamente,
      Sistema Financeiro IG-UNICAMP
    `;

    // Envia para cada destinatário
    emails.forEach(email => {
      GmailApp.sendEmail(email, subject, body);
      Logger.log(`Email de notificação enviado para ${email}`);
    });

  } catch (error) {
    Logger.log('Erro ao enviar email de notificação: ' + error.toString());
  }
}


/**
 * Essa função varre toda a planilha e insere um ID
 * em qualquer linha que ainda não tenha.
 * Útil para dados antigos ou caso a planilha tenha linhas manualmente inseridas.
 *
 * Você pode acionar esta função manualmente ou criar um gatilho onOpen/onEdit
 * que chame esta função.
 */
function fillAllMissingIds() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Descobre em qual coluna está "Id"
  var colId = findIdColumnIndex(sheet);
  if (colId <= 0) {
    SpreadsheetApp.getUi().alert("Não encontrei a coluna 'Id'. Verifique o cabeçalho.");
    return;
  }

  // Determina o total de linhas
  var lastRow = sheet.getLastRow();
  // Se desejar ignorar a linha de cabeçalho, inicie do row=2
  for (var row = 2; row <= lastRow; row++) {
    var cellValue = sheet.getRange(row, colId).getValue();
    if (!cellValue) {
      // Não tem ID, gera um ID único
      var newId = generateUniqueId(sheet);
      sheet.getRange(row, colId).setValue(newId);
    }
  }
  SpreadsheetApp.getUi().alert("IDs preenchidos onde estavam faltando.");
}

/**
 * Gera um ID no formato "YYYY - 000X" que não exista ainda na coluna "Id".
 * Utiliza uma propriedade do script ("NEXT_ID") para saber o último valor usado,
 * mas, além disso, confere duplicatas (por segurança).
 */
function generateUniqueId(sheet) {
  var scriptProperties = PropertiesService.getScriptProperties();
  var nextValueStr = scriptProperties.getProperty("NEXT_ID");
  if (!nextValueStr) {
    nextValueStr = "1";
  }
  var nextValue = parseInt(nextValueStr, 10);

  while (true) {
    var year = new Date().getFullYear();
    var tentativeId = year + " - " + Utilities.formatString("%04d", nextValue);

    // Verifica se "tentativeId" já existe
    if (!idExists(sheet, tentativeId)) {
      // Se não existe, este ID é válido
      // Incrementa e salva no Script Properties
      scriptProperties.setProperty("NEXT_ID", (nextValue + 1).toString());
      return tentativeId;
    } else {
      // Se já existe, incrementa e tenta de novo
      nextValue++;
    }
  }
}

/**
 * Função auxiliar para conferir se um ID já está presente na coluna "Id".
 */
function idExists(sheet, candidateId) {
  var colId = findIdColumnIndex(sheet);
  if (colId <= 0) return false;

  // Lê toda a coluna "Id" em forma de array bidimensional
  var range = sheet.getRange(2, colId, sheet.getLastRow() - 1, 1); // inicia em linha 2
  var values = range.getValues(); // array Nx1

  for (var i = 0; i < values.length; i++) {
    if (String(values[i][0]) === String(candidateId)) {
      return true;
    }
  }
  return false;
}

/**
 * Acha o índice (coluna) onde está o cabeçalho "Id" na primeira linha.
 * Retorna 0 se não encontrar.
 */
function findIdColumnIndex(sheet) {
  var headerRowValues = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  // Procura "Id" (exatamente) ou se quiser case-insensitive, adapte.
  var colIndex = headerRowValues.indexOf("Id") + 1;
  return colIndex; // se não encontrou, será 0
}
