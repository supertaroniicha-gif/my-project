/**
 * ガイアくん オリエンテーション フィードバック管理システム
 * Google Apps Script
 *
 * 機能:
 * - Good/More ラベル管理
 * - Next Action 記録（2つ）
 * - 複数回のFB統計
 * - 自動集計＆グラフ生成
 */

// スプレッドシートの設定
const SHEET_ID = 'スプレッドシートID'; // 実際のIDに置き換え
const FEEDBACK_SHEET = 'フィードバック入力';
const STATS_SHEET = '統計ダッシュボード';

/**
 * 初期化: シートの構造を作成
 */
function initializeSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // フィードバック入力シートの作成/更新
  let feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  if (!feedbackSheet) {
    feedbackSheet = ss.insertSheet(FEEDBACK_SHEET);
  }

  // ヘッダー行設定
  const headers = ['日付', 'Good/More', '項目', '詳細', 'Next Action①', 'Next Action②', 'FB回数'];
  feedbackSheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // ヘッダーのフォーマット
  const headerRange = feedbackSheet.getRange(1, 1, 1, headers.length);
  headerRange.setFontWeight('bold');
  headerRange.setBackground('#1F4E78');
  headerRange.setFontColor('white');
  headerRange.setHorizontalAlignment('center');

  // 列幅設定
  feedbackSheet.setColumnWidth(1, 100);  // 日付
  feedbackSheet.setColumnWidth(2, 100);  // Good/More
  feedbackSheet.setColumnWidth(3, 120);  // 項目
  feedbackSheet.setColumnWidth(4, 200);  // 詳細
  feedbackSheet.setColumnWidth(5, 150);  // Next Action①
  feedbackSheet.setColumnWidth(6, 150);  // Next Action②
  feedbackSheet.setColumnWidth(7, 80);   // FB回数

  // Good/More のデータ検証（プルダウン）
  const dv = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Good', 'More'], true)
    .build();
  feedbackSheet.getRange('B2:B101').setDataValidation(dv);

  // 統計ダッシュボードシートの作成/更新
  let statsSheet = ss.getSheetByName(STATS_SHEET);
  if (!statsSheet) {
    statsSheet = ss.insertSheet(STATS_SHEET);
  }

  updateStatistics();
}

/**
 * フィードバック入力時の自動カラーコーディング
 */
function onEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();
  const col = range.getColumn();

  // Good/More 列（B列）の色分け
  if (sheet.getName() === FEEDBACK_SHEET && col === 2) {
    const row = range.getRow();
    if (row > 1) {
      const value = range.getValue();
      let color = '#FFFFFF';

      if (value === 'Good') {
        color = '#D4EDDA'; // 薄い緑
      } else if (value === 'More') {
        color = '#FFF3CD'; // 薄いオレンジ
      }

      range.setBackground(color);
    }
  }
}

/**
 * 統計情報を更新
 */
function updateStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const feedbackSheet = ss.getSheetByName(FEEDBACK_SHEET);
  const statsSheet = ss.getSheetByName(STATS_SHEET);

  if (!feedbackSheet || !statsSheet) return;

  // フィードバックデータを取得
  const data = feedbackSheet.getRange('A2:G101').getValues();
  const feedbacks = data.filter(row => row[0] !== ''); // 空行を除外

  // Good/More の集計
  const goodCount = feedbacks.filter(row => row[1] === 'Good').length;
  const moreCount = feedbacks.filter(row => row[1] === 'More').length;
  const totalCount = goodCount + moreCount;

  // Next Action の集計
  const nextActions = {};
  feedbacks.forEach(row => {
    [row[4], row[5]].forEach(action => {
      if (action && action.trim() !== '') {
        nextActions[action] = (nextActions[action] || 0) + 1;
      }
    });
  });

  // 統計ダッシュボードをクリア
  statsSheet.clear();

  // タイトル
  statsSheet.getRange('A1').setValue('📊 フィードバック統計ダッシュボード');
  statsSheet.getRange('A1').setFontSize(16).setFontWeight('bold');

  // サマリー統計
  let row = 3;
  statsSheet.getRange(row, 1).setValue('総フィードバック数');
  statsSheet.getRange(row, 2).setValue(totalCount);
  row++;

  statsSheet.getRange(row, 1).setValue('Good 数');
  statsSheet.getRange(row, 2).setValue(goodCount);
  statsSheet.getRange(row, 2).setBackground('#D4EDDA');
  row++;

  statsSheet.getRange(row, 1).setValue('More 数');
  statsSheet.getRange(row, 2).setValue(moreCount);
  statsSheet.getRange(row, 2).setBackground('#FFF3CD');
  row++;

  if (totalCount > 0) {
    statsSheet.getRange(row, 1).setValue('Good 率 (%)');
    statsSheet.getRange(row, 2).setValue(Math.round(goodCount / totalCount * 100));
    row++;

    statsSheet.getRange(row, 1).setValue('More 率 (%)');
    statsSheet.getRange(row, 2).setValue(Math.round(moreCount / totalCount * 100));
    row++;
  }

  // Next Action ランキング
  row += 2;
  statsSheet.getRange(row, 1).setValue('Next Action ランキング');
  statsSheet.getRange(row, 1).setFontWeight('bold').setBackground('#E8F0FE');

  row++;
  statsSheet.getRange(row, 1).setValue('項目');
  statsSheet.getRange(row, 2).setValue('頻度');
  statsSheet.getRange(row, 1, 1, 2).setFontWeight('bold').setBackground('#F3F3F3');

  // ソートして上位表示
  const sortedActions = Object.entries(nextActions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10); // Top 10

  sortedActions.forEach(([action, count]) => {
    row++;
    statsSheet.getRange(row, 1).setValue(action);
    statsSheet.getRange(row, 2).setValue(count);
  });

  // フィードバック回数別の分析
  row += 3;
  statsSheet.getRange(row, 1).setValue('フィードバック回数別');
  statsSheet.getRange(row, 1).setFontWeight('bold').setBackground('#E8F0FE');

  row++;
  statsSheet.getRange(row, 1).setValue('回数');
  statsSheet.getRange(row, 2).setValue('件数');
  statsSheet.getRange(row, 1, 1, 2).setFontWeight('bold').setBackground('#F3F3F3');

  // 回数ごとの集計
  const fbCounts = {};
  feedbacks.forEach(row => {
    const count = row[6] || '1';
    fbCounts[count] = (fbCounts[count] || 0) + 1;
  });

  Object.keys(fbCounts).sort().forEach(count => {
    row++;
    statsSheet.getRange(row, 1).setValue(`${count}回目`);
    statsSheet.getRange(row, 2).setValue(fbCounts[count]);
  });

  // 列幅設定
  statsSheet.setColumnWidth(1, 200);
  statsSheet.setColumnWidth(2, 100);
}

/**
 * メニューに追加する関数
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('フィードバック管理')
    .addItem('初期化', 'initializeSheet')
    .addItem('統計を更新', 'updateStatistics')
    .addSeparator()
    .addItem('ヘルプ', 'showHelp')
    .addToUi();
}

/**
 * ヘルプを表示
 */
function showHelp() {
  const html = HtmlService.createHtmlOutput(`
    <h2>フィードバック管理システム ヘルプ</h2>
    <h3>使い方:</h3>
    <ul>
      <li><b>日付</b>: フィードバックの日付を入力</li>
      <li><b>Good/More</b>: ドロップダウンから選択</li>
      <li><b>項目</b>: フィードバックの項目</li>
      <li><b>詳細</b>: 詳しい内容</li>
      <li><b>Next Action①②</b>: 実行すべき次のアクション</li>
      <li><b>FB回数</b>: 何回目のフィードバックか（1, 2, 3...）</li>
    </ul>
    <h3>機能:</h3>
    <ul>
      <li>Good/More は自動で色分けされます</li>
      <li>統計ダッシュボードで自動集計します</li>
      <li>「統計を更新」ボタンで手動更新可能</li>
    </ul>
  `);

  SpreadsheetApp.getUi().showModelessDialog(html, 'ヘルプ');
}

/**
 * トリガーを設定（自動更新）
 */
function setTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'updateStatistics') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 新しいトリガーを設定（15分ごと）
  ScriptApp.newTrigger('updateStatistics')
    .timeBased()
    .everyMinutes(15)
    .create();
}
