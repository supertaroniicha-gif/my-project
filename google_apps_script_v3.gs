const FEEDBACK_SHEET = 'フィードバック入力';
const STATS_SHEET = '統計ダッシュボード';

// 現在のシート列構成:
// A:日付 | B:Good/More | C:項目 | D:詳細 | E:Next Action① | F:Next Action② | G:FB回数 | H:メモ

const ITEMS = [
  'アイスブレイク',
  'ヒアリング',
  'NVC',
  '提案',
  '料金折衝',
  'コミュニケーション',
  '目標設定',
  '深掘り'
];

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
  '自分も楽しく',
  '下げたら上げる',
  'うまくいったとき、そうでないときの差',
  'テスト成績分析',
  '得意科目活用',
  '苦手科目克服',
  '時間管理指導',
  '親子間コミュニケーション',
  'ADHD対応',
  '字の書き方指導',
  '途中式指導',
  '集中力向上',
  '動機付け強化',
  '未来像共有',
  '小さな成功体験',
  'フィードバックの具体性',
  '行動分析',
  '思考パターン改善'
];

function initializeSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // フィードバック入力シート
  let feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  if (!feedbackSheet) {
    feedbackSheet = ss.insertSheet(FEEDBACK_SHEET);
  }

  // ヘッダー設定
  const headers = ['日付', 'Good/More', '項目', '詳細', 'Next Action①', 'Next Action②', 'FB回数', 'メモ'];
  feedbackSheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // ヘッダーのスタイル
  const headerRange = feedbackSheet.getRange(1, 1, 1, headers.length);
  headerRange
    .setBackground('#1F4E78')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setFontSize(11)
    .setVerticalAlignment('middle')
    .setHorizontalAlignment('center');
  feedbackSheet.setRowHeight(1, 40);

  // 列幅最適化
  feedbackSheet.setColumnWidth(1, 110);  // 日付
  feedbackSheet.setColumnWidth(2, 100);  // Good/More
  feedbackSheet.setColumnWidth(3, 130);  // 項目
  feedbackSheet.setColumnWidth(4, 280);  // 詳細
  feedbackSheet.setColumnWidth(5, 180);  // Next Action①
  feedbackSheet.setColumnWidth(6, 180);  // Next Action②
  feedbackSheet.setColumnWidth(7, 80);   // FB回数
  feedbackSheet.setColumnWidth(8, 220);  // メモ

  // 既存データの色を再適用
  applyColorToExistingData(feedbackSheet);

  // ドロップダウン: Good/More (B列)
  const goodMoreDV = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Good', 'More'], true)
    .build();
  feedbackSheet.getRange('B2:B200').setDataValidation(goodMoreDV);

  // ドロップダウン: 項目 (C列)
  const itemDV = SpreadsheetApp.newDataValidation()
    .requireValueInList(ITEMS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('C2:C200').setDataValidation(itemDV);

  // ドロップダウン: Next Action① (E列)
  const nextActionDV1 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('E2:E200').setDataValidation(nextActionDV1);

  // ドロップダウン: Next Action② (F列)
  const nextActionDV2 = SpreadsheetApp.newDataValidation()
    .requireValueInList(NEXT_ACTIONS, true)
    .setAllowInvalid(true)
    .build();
  feedbackSheet.getRange('F2:F200').setDataValidation(nextActionDV2);

  // 統計ダッシュボードシート
  let statsSheet = ss.getSheetByName(STATS_SHEET);
  if (!statsSheet) {
    statsSheet = ss.insertSheet(STATS_SHEET);
  }

  updateStatistics();

  SpreadsheetApp.getUi().alert('✅ 初期化完了！\nドロップダウンと色分けが設定されました。');
}

function applyColorToExistingData(feedbackSheet) {
  const lastRow = feedbackSheet.getLastRow();
  if (lastRow < 2) return;

  const goodFill = '#D4EDDA';
  const moreFill = '#FFF3CD';

  for (let r = 2; r <= lastRow; r++) {
    const cell = feedbackSheet.getRange(r, 2);
    const val = cell.getValue();
    if (val === 'Good') {
      cell.setBackground(goodFill).setFontColor('#155724').setFontWeight('bold');
    } else if (val === 'More') {
      cell.setBackground(moreFill).setFontColor('#856404').setFontWeight('bold');
    }
    feedbackSheet.setRowHeight(r, 35);
  }
}

function onEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();

  if (sheet.getName() !== FEEDBACK_SHEET) return;

  const row = range.getRow();
  const col = range.getColumn();

  if (row === 1) return;

  // Good/More (B列=2) の色分け
  if (col === 2) {
    const value = range.getValue();
    if (value === 'Good') {
      range.setBackground('#D4EDDA').setFontColor('#155724').setFontWeight('bold');
    } else if (value === 'More') {
      range.setBackground('#FFF3CD').setFontColor('#856404').setFontWeight('bold');
    } else {
      range.setBackground('#FFFFFF').setFontColor('#000000').setFontWeight('normal');
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

  const allData = feedbackSheet.getRange('A2:H200').getValues();
  const feedbacks = allData.filter(row => row[0] !== '' && row[1] !== '');

  statsSheet.clear();

  if (feedbacks.length === 0) {
    statsSheet.getRange('A1').setValue('データを入力してください');
    return;
  }

  const goodCount = feedbacks.filter(row => row[1] === 'Good').length;
  const moreCount = feedbacks.filter(row => row[1] === 'More').length;
  const totalCount = goodCount + moreCount;

  // 項目別集計
  const itemStats = {};
  feedbacks.forEach(row => {
    const item = row[2] || '未分類';
    if (!itemStats[item]) itemStats[item] = { good: 0, more: 0 };
    if (row[1] === 'Good') itemStats[item].good++;
    if (row[1] === 'More') itemStats[item].more++;
  });

  // Next Action集計
  const nextActions = {};
  feedbacks.forEach(row => {
    [row[4], row[5]].forEach(action => {
      if (action && action.trim() !== '') {
        const a = action.trim();
        nextActions[a] = (nextActions[a] || 0) + 1;
      }
    });
  });

  // ===== 統計ダッシュボード描画 =====
  let r = 1;

  // タイトル
  statsSheet.getRange(r, 1, 1, 4).merge()
    .setValue('📊 フィードバック統計ダッシュボード')
    .setFontSize(16).setFontWeight('bold')
    .setBackground('#1F4E78').setFontColor('#FFFFFF')
    .setHorizontalAlignment('center').setVerticalAlignment('middle');
  statsSheet.setRowHeight(r, 45);
  r += 2;

  // サマリーセクション
  statsSheet.getRange(r, 1, 1, 2).setValues([['📈 サマリー', '']])
    .setFontWeight('bold').setFontSize(12)
    .setBackground('#E8F0FE');
  r++;

  const summaryData = [
    ['総フィードバック数', totalCount],
    ['Good 数', goodCount],
    ['More 数', moreCount],
    ['Good 率 (%)', totalCount > 0 ? Math.round(goodCount / totalCount * 100) + '%' : '-'],
    ['More 率 (%)', totalCount > 0 ? Math.round(moreCount / totalCount * 100) + '%' : '-'],
  ];
  summaryData.forEach(([label, val], i) => {
    statsSheet.getRange(r, 1).setValue(label).setFontWeight('bold');
    const valCell = statsSheet.getRange(r, 2).setValue(val);
    if (label === 'Good 数' || label === 'Good 率 (%)') valCell.setBackground('#D4EDDA').setFontWeight('bold');
    if (label === 'More 数' || label === 'More 率 (%)') valCell.setBackground('#FFF3CD').setFontWeight('bold');
    r++;
  });
  r++;

  // 項目別集計セクション
  statsSheet.getRange(r, 1, 1, 3).setValues([['🗂️ 項目別 Good/More', '', '']])
    .setFontWeight('bold').setFontSize(12)
    .setBackground('#E8F0FE');
  r++;

  statsSheet.getRange(r, 1, 1, 3).setValues([['項目', 'Good', 'More']])
    .setFontWeight('bold').setBackground('#F3F3F3');
  r++;

  Object.entries(itemStats).sort((a, b) => (b[1].good + b[1].more) - (a[1].good + a[1].more)).forEach(([item, cnt]) => {
    statsSheet.getRange(r, 1).setValue(item);
    statsSheet.getRange(r, 2).setValue(cnt.good).setBackground('#D4EDDA');
    statsSheet.getRange(r, 3).setValue(cnt.more).setBackground('#FFF3CD');
    r++;
  });
  r++;

  // Next Action ランキング
  statsSheet.getRange(r, 1, 1, 2).setValues([['🏆 Next Action ランキング', '']])
    .setFontWeight('bold').setFontSize(12)
    .setBackground('#E8F0FE');
  r++;

  statsSheet.getRange(r, 1, 1, 2).setValues([['アクション', '頻度']])
    .setFontWeight('bold').setBackground('#F3F3F3');
  r++;

  Object.entries(nextActions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .forEach(([action, count]) => {
      statsSheet.getRange(r, 1).setValue(action);
      statsSheet.getRange(r, 2).setValue(count).setBackground('#FFF9E6');
      r++;
    });

  // 列幅設定
  statsSheet.setColumnWidth(1, 260);
  statsSheet.setColumnWidth(2, 80);
  statsSheet.setColumnWidth(3, 80);
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('フィードバック管理')
    .addItem('🔧 初期化（初回セットアップ）', 'initializeSheet')
    .addItem('📊 統計を更新', 'updateStatistics')
    .addItem('🎨 色を再適用', 'reapplyColors')
    .addToUi();
}

function reapplyColors() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  if (feedbackSheet) {
    applyColorToExistingData(feedbackSheet);
    SpreadsheetApp.getUi().alert('✅ 色の再適用が完了しました！');
  }
}
