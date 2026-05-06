const FEEDBACK_SHEET = 'フィードバック入力';
const STATS_SHEET = '統計ダッシュボード';

// Next Action の推奨選択肢（ガイアくんのFBから）
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

  const headers = ['日付', 'Good/More', '項目', '詳細', 'Next Action①', 'Next Action②', 'FB回数'];
  feedbackSheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  const headerRange = feedbackSheet.getRange(1, 1, 1, headers.length);
  headerRange.setFontWeight('bold').setBackground('#1F4E78').setFontColor('white');
  headerRange.setVerticalAlignment('middle');

  feedbackSheet.setColumnWidth(1, 100);
  feedbackSheet.setColumnWidth(2, 100);
  feedbackSheet.setColumnWidth(3, 120);
  feedbackSheet.setColumnWidth(4, 200);
  feedbackSheet.setColumnWidth(5, 180);
  feedbackSheet.setColumnWidth(6, 180);
  feedbackSheet.setColumnWidth(7, 80);

  // Good/More のデータ検証（プルダウン）
  const goodMoreDV = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Good', 'More'], true)
    .build();
  feedbackSheet.getRange('B2:B101').setDataValidation(goodMoreDV);

  // Next Action① のデータ検証（プルダウン）
  const nextActionDV1 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('E2:E101').setDataValidation(nextActionDV1);

  // Next Action② のデータ検証（プルダウン）
  const nextActionDV2 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('F2:F101').setDataValidation(nextActionDV2);

  let statsSheet = ss.getSheetByName(STATS_SHEET);
  if (!statsSheet) {
    statsSheet = ss.insertSheet(STATS_SHEET);
  }

  updateStatistics();
}

function onEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();

  // Good/More 列の色分け
  if (sheet.getName() === FEEDBACK_SHEET && range.getColumn() === 2) {
    const value = range.getValue();
    if (value === 'Good') {
      range.setBackground('#D4EDDA');
    } else if (value === 'More') {
      range.setBackground('#FFF3CD');
    }
  }

  // 統計を自動更新
  updateStatistics();
}

function updateStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  const statsSheet = ss.getSheetByName(STATS_SHEET);

  if (!feedbackSheet || !statsSheet) return;

  // フィードバックデータを取得
  const allData = feedbackSheet.getRange('A2:G101').getValues();
  const feedbacks = allData.filter(row => row[0] !== '' && row[1] !== '');

  if (feedbacks.length === 0) {
    statsSheet.clear();
    statsSheet.getRange('A1').setValue('データを入力してください');
    return;
  }

  // Good/More の集計
  const goodCount = feedbacks.filter(row => row[1] === 'Good').length;
  const moreCount = feedbacks.filter(row => row[1] === 'More').length;
  const totalCount = goodCount + moreCount;

  // Next Action の集計（正規化：前後の空白を削除）
  const nextActions = {};
  feedbacks.forEach(row => {
    [row[4], row[5]].forEach(action => {
      if (action && action.trim() !== '') {
        const normalizedAction = action.trim();
        nextActions[normalizedAction] = (nextActions[normalizedAction] || 0) + 1;
      }
    });
  });

  // 統計ダッシュボード更新
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
