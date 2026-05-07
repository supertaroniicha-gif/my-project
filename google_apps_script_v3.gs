const FEEDBACK_SHEET = 'フィードバック入力';
const STATS_SHEET = '統計ダッシュボード';

const ITEMS = ['アイスブレイク', 'ヒアリング', '提案', '料金折衝', 'コミュニケーション'];

const NEXT_ACTIONS = [
  'アイスブレイク拡張',
  '深掘り強化',
  '質問形式工夫',
  'スキル訓練',
  'コミュニケーション強化',
  '共感重視',
  '定量データ活用',
  'ヒアリング深化',
  '目標設定共有',
  '笑顔増加',
  '説得フロー改善',
  '権威性活用',
  '安心感提供',
  '親和性向上',
  'ネック潰し',
  '自己紹介改善',
  'Open Question調整',
  'Yes/No質問活用',
  '心理的安全性確保',
  '環境設定改善',
  '深層心理への到達',
  '比較分析強化',
  '課題回避パターン認識',
  '学習習慣形成',
  '褒める+共感',
  '間接共感活用',
  '価値訴求配置',
  '段階的説得',
  'ラポール深化',
  '信頼構築',
  'テスト成績分析',
  '得意科目活用',
  '苦手科目克服',
  '時間管理指導',
  '親子間コミュニケーション',
  'ADHD対応',
  '字の書き方指導',
  '途中式指導',
  'メモリ運用改善',
  '集中力向上',
  '動機付け強化',
  'ロールモデル提示',
  '未来像共有',
  '小さな成功体験',
  '褒める タイミング調整',
  'フィードバックの具体性',
  '行動分析',
  '思考パターン改善'
];

function initializeSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  let feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  if (!feedbackSheet) {
    feedbackSheet = ss.insertSheet(FEEDBACK_SHEET);
  }

  const headers = ['日付', '曜日', '項目', 'Good/More', '詳細', 'Next Action①', 'Next Action②', 'FB回数'];
  feedbackSheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  const headerRange = feedbackSheet.getRange(1, 1, 1, headers.length);
  headerRange.setFontWeight('bold').setBackground('#1F4E78').setFontColor('white');
  headerRange.setVerticalAlignment('middle');

  // Set column widths
  feedbackSheet.setColumnWidth(1, 100);  // 日付
  feedbackSheet.setColumnWidth(2, 80);   // 曜日
  feedbackSheet.setColumnWidth(3, 120);  // 項目
  feedbackSheet.setColumnWidth(4, 100);  // Good/More
  feedbackSheet.setColumnWidth(5, 200);  // 詳細
  feedbackSheet.setColumnWidth(6, 180);  // Next Action①
  feedbackSheet.setColumnWidth(7, 180);  // Next Action②
  feedbackSheet.setColumnWidth(8, 80);   // FB回数

  // Data validation for Good/More (Column D)
  const goodMoreDV = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Good', 'More'], true)
    .build();
  feedbackSheet.getRange('D2:D101').setDataValidation(goodMoreDV);

  // Data validation for Item (Column C)
  const itemDV = SpreadsheetApp.newDataValidation()
    .requireValueInList(ITEMS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('C2:C101').setDataValidation(itemDV);

  // Data validation for Next Action① (Column F)
  const nextActionDV1 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('F2:F101').setDataValidation(nextActionDV1);

  // Data validation for Next Action② (Column G)
  const nextActionDV2 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('G2:G101').setDataValidation(nextActionDV2);

  let statsSheet = ss.getSheetByName(STATS_SHEET);
  if (!statsSheet) {
    statsSheet = ss.insertSheet(STATS_SHEET);
  }

  updateStatistics();
}

function onEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();

  if (sheet.getName() !== FEEDBACK_SHEET) return;

  const row = range.getRow();
  const col = range.getColumn();

  if (row === 1) return; // Skip header row

  // Auto-fill day of week when date is entered in column A
  if (col === 1) {
    const dateValue = range.getValue();
    if (dateValue && dateValue instanceof Date) {
      const dayOfWeek = ['日', '月', '火', '水', '木', '金', '土'][dateValue.getDay()];
      sheet.getRange(row, 2).setValue(dayOfWeek);
    }
  }

  // Color coding for Good/More (Column D)
  if (col === 4) {
    const value = range.getValue();
    if (value === 'Good') {
      range.setBackground('#D4EDDA');
      range.setFontColor('#155724');
    } else if (value === 'More') {
      range.setBackground('#FFF3CD');
      range.setFontColor('#856404');
    } else {
      range.setBackground('#FFFFFF');
    }
    range.setFontWeight('bold');
  }

  // Auto-update statistics
  updateStatistics();
}

function updateStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  const statsSheet = ss.getSheetByName(STATS_SHEET);

  if (!feedbackSheet || !statsSheet) return;

  // Get feedback data (columns A-H, rows 2-101)
  const allData = feedbackSheet.getRange('A2:H101').getValues();
  const feedbacks = allData.filter(row => row[0] !== '' && row[3] !== '');

  if (feedbacks.length === 0) {
    statsSheet.clear();
    statsSheet.getRange('A1').setValue('データを入力してください');
    return;
  }

  // Count Good/More (column D is index 3)
  const goodCount = feedbacks.filter(row => row[3] === 'Good').length;
  const moreCount = feedbacks.filter(row => row[3] === 'More').length;
  const totalCount = goodCount + moreCount;

  // Aggregate Next Actions (columns F and G are indices 5 and 6)
  const nextActions = {};
  feedbacks.forEach(row => {
    [row[5], row[6]].forEach(action => {
      if (action && action.trim() !== '') {
        const normalizedAction = action.trim();
        nextActions[normalizedAction] = (nextActions[normalizedAction] || 0) + 1;
      }
    });
  });

  // Clear and update stats sheet
  statsSheet.clear();

  let row = 1;
  statsSheet.getRange(row, 1, 1, 2).setValues([['📊 統計ダッシュボード', '']]);
  statsSheet.getRange(row, 1).setFontSize(14).setFontWeight('bold');

  row = 3;
  statsSheet.getRange(row, 1, 1, 2).setValues([['総フィードバック数', totalCount]]);
  statsSheet.getRange(row, 1).setFontWeight('bold');
  row++;

  statsSheet.getRange(row, 1, 1, 2).setValues([['Good数', goodCount]]);
  statsSheet.getRange(row, 2).setBackground('#D4EDDA').setFontWeight('bold');
  row++;

  statsSheet.getRange(row, 1, 1, 2).setValues([['More数', moreCount]]);
  statsSheet.getRange(row, 2).setBackground('#FFF3CD').setFontWeight('bold');
  row++;

  if (totalCount > 0) {
    statsSheet.getRange(row, 1, 1, 2).setValues([['Good率(%)', Math.round(goodCount / totalCount * 100)]]);
  }

  // Next Action ランキング
  row += 2;
  statsSheet.getRange(row, 1, 1, 2).setValues([['Next Action ランキング', '']]);
  statsSheet.getRange(row, 1, 1, 2).setFontWeight('bold').setBackground('#E8F0FE');

  row++;
  statsSheet.getRange(row, 1, 1, 2).setValues([['項目', '頻度']]);
  statsSheet.getRange(row, 1, 1, 2).setFontWeight('bold').setBackground('#F3F3F3');

  const sortedActions = Object.entries(nextActions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15);

  sortedActions.forEach(([action, count]) => {
    row++;
    statsSheet.getRange(row, 1, 1, 2).setValues([[action, count]]);
    if (count > 0) {
      statsSheet.getRange(row, 2).setBackground('#FFF9E6');
    }
  });

  statsSheet.setColumnWidth(1, 250);
  statsSheet.setColumnWidth(2, 100);
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('フィードバック管理')
    .addItem('初期化', 'initializeSheet')
    .addItem('統計を更新', 'updateStatistics')
    .addToUi();
}
