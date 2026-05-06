#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ガイアくんのオリエンテーション フィードバック分析 Excel生成
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Excelワークブック作成
wb = Workbook()
ws = wb.active
ws.title = "フィードバック分析"

# 列幅設定
ws.column_dimensions['A'].width = 12
ws.column_dimensions['B'].width = 20
ws.column_dimensions['C'].width = 45
ws.column_dimensions['D'].width = 10
ws.column_dimensions['E'].width = 12
ws.column_dimensions['F'].width = 20

# ヘッダー行を設定
headers = ['カテゴリ', '項目', '詳細', '重要度', '対象', '関連する課題']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col)
    cell.value = header
    cell.font = Font(bold=True, color="FFFFFF", size=11)
    cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# データ定義
data = [
    # Good項目
    ['Good', 'コミュニケーション', '教育プランナーが父にも子供にも話し掛け・目線を合わせた', '高', '親子', '信頼構築'],
    ['Good', '心理的配慮', '褒めるだけでなく共感を重視', '高', '生徒', 'ラポール形成'],
    ['Good', 'ニーズ把握', '生徒のネック（怒られるのが怖い）を抽出し潰せた', '高', '生徒', '学習ブロック除去'],
    ['Good', '共感スキル', '自分の経験を話した（間接共感）', '中', '生徒', '信頼構築'],
    ['Good', '権威性・専門性', '大学名での権威性が刺さった', '高', '親子', '納得感・信頼'],
    ['Good', '安心感提供', '全体フロー説明で進め方の見通しを立てた', '高', '親子', '不安軽減'],
    ['Good', '親和性', '自己紹介で「恥ずかしくない」という寄り添いを示した', '中', '生徒', 'リラックス効果'],
    ['Good', '深掘りスキル', '好きなことを起点に話を展開した', '中', '生徒', '興味・動機づけ'],
    ['Good', '定量的説明', '定量データ（テスト成績80-90 vs 50-60）を提示', '高', '親子', '客観的納得感'],
    ['Good', 'ヒアリング', 'お子さん/親御さんのどちらが主導で探しているか確認', '高', '親子', '提案方向の最適化'],
    ['Good', '時間活用', '勉強時間の使い方を早期に話題化', '中', '生徒', '実行性確保'],

    # More項目
    ['More', 'アイスブレイク', 'いきなり終わらせるのはもったいない（もっと拡げる余地あり）', '中', '生徒', 'ラポール深化'],
    ['More', 'グループ面談の環境設定', '1:2設定で受験生だと質問しづらい潰し感が出ていた', '中', '生徒', '心理的安全性'],
    ['More', '目標設定', '目標を教育プランナーと過程で合わせられなかった', '高', '親子', '納得感・方向性'],
    ['More', '勉強内容の深掘り', '毎回勉強について深掘りが不足', '高', '生徒', '学習課題の本質把握'],
    ['More', '価値訴求の配置', '1:1の価値訴求を3-4箇所で入れられると良い', '中', '親子', '説得力・納得'],
    ['More', '質問形式', 'ADHD傾向の子にはOpen Question苦手→Yes/No質問が有効', '高', '生徒', '回答容易性'],
    ['More', '深堀りの浅さ', '好きなことが表層的（ドッジボール→避けるのが得意 止まり）', '中', '生徒', '深層心理・本質理解'],
    ['More', '非言語コミュニケーション', '笑顔が前回より減った（フラットになった）', '中', '生徒', '親和性・ラポール'],
    ['More', '説得フロー', '1課題に1トライの良さをすぐぶつけるのはきつい→もっと頷いてから最後に', '高', '親子', '納得感・段階性'],
    ['More', '聴くべき深さ', 'この状態でプランニング行くと納得感がない→もっと聴くべき', '高', '生徒', '本当の課題解決'],
    ['More', '深層心理への到達', '字が汚い→途中式が書けない など深層原因を掘り下げる必要', '高', '生徒', '根本的な学習課題把握'],
    ['More', '比較分析', '他にできている科目がなぜできているのか、苦手科目では何ができていないか', '高', '生徒', '強み活用・弱点把握'],
    ['More', '課題回避パターン', '難しい課題から逃げている傾向（ADHD傾向）を早期把握', '高', '生徒', '学習習慣形成の課題'],
]

# カラー定義
good_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")  # 薄い緑
more_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")   # 薄いオレンジ

high_importance_fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")  # 薄い赤

# ボーダー設定
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# データ行を追加
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.value = value
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        # セルの高さを自動調整
        ws.row_dimensions[row_idx].height = 30

        # カテゴリ別の背景色
        if col_idx == 1:  # カテゴリ列
            if value == 'Good':
                cell.fill = good_fill
                cell.font = Font(bold=True, color="155724")
            else:  # More
                cell.fill = more_fill
                cell.font = Font(bold=True, color="856404")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # 重要度別の背景色
        elif col_idx == 4:  # 重要度列
            if value == '高':
                cell.fill = high_importance_fill
                cell.font = Font(bold=True, color="721C24")
            cell.alignment = Alignment(horizontal="center", vertical="center")

# 統計情報シートを追加
ws2 = wb.create_sheet("統計情報")

# 統計データ
good_count = sum(1 for row in data if row[0] == 'Good')
more_count = sum(1 for row in data if row[0] == 'More')
high_count = sum(1 for row in data if row[3] == '高')

stats = [
    ['総数', len(data)],
    ['Good項目数', good_count],
    ['More項目数', more_count],
    ['高重要度項目数', high_count],
]

# 統計ヘッダー
for col, header in enumerate(['項目', '数'], 1):
    cell = ws2.cell(row=1, column=col)
    cell.value = header
    cell.font = Font(bold=True, color="FFFFFF", size=11)
    cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")

ws2.column_dimensions['A'].width = 20
ws2.column_dimensions['B'].width = 15

# 統計データ行
for row_idx, stat_row in enumerate(stats, 2):
    for col_idx, value in enumerate(stat_row, 1):
        cell = ws2.cell(row=row_idx, column=col_idx)
        cell.value = value
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if col_idx == 1:
            cell.font = Font(bold=True)

# ファイルを保存
output_file = '/home/user/my-project/gaia-kun-orientation-feedback.xlsx'
wb.save(output_file)

print(f"✅ Excelファイルが作成されました！")
print(f"📄 ファイル: {output_file}")
print(f"📊 統計:")
print(f"   - 総フィードバック数: {len(data)}")
print(f"   - Good項目: {good_count}")
print(f"   - More項目: {more_count}")
print(f"   - 高重要度: {high_count}")
