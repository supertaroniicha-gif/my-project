import zipfile, os

cards = [
    {"No":1,"会社名":"株式会社山田商事","部署":"営業部","役職":"部長","氏名":"山田太郎","住所":"東京都千代田区丸の内1-2-3","TEL":"03-1234-5678","Email":"taro.yamada@yamada-shoji.co.jp"},
    {"No":2,"会社名":"株式会社フューチャーラボ","部署":"研究開発部","役職":"研究員","氏名":"松本理恵","住所":"東京都文京区本郷25-26-27","TEL":"03-1111-2222","Email":"rie.matsumoto@futurelab.co.jp"},
    {"No":3,"会社名":"有限会社丸山建設","部署":"工事部","役職":"現場監督","氏名":"丸山幸治","住所":"埼玉県さいたま市大宮区桜木町28-29","TEL":"048-3333-4444","Email":"koji.maruyama@maruyama-kensetsu.jp"},
    {"No":4,"会社名":"株式会社スターデザイン","部署":"","役職":"アートディレクター","氏名":"中村あゆみ","住所":"東京都目黒区自由が丘30-31","TEL":"03-5555-6666","Email":"ayumi.nakamura@stardesign.co.jp"},
    {"No":5,"会社名":"社会福祉法人あおぞら","部署":"介護部","役職":"介護福祉士","氏名":"井上雄太","住所":"兵庫県神戸市中央区三宮32-33","TEL":"078-7777-8888","Email":"yuta.inoue@aozora-welfare.jp"},
    {"No":6,"会社名":"株式会社ノースウィンド","部署":"物流部","役職":"部長代理","氏名":"木村真理子","住所":"宮城県仙台市青葉区一番町34-35","TEL":"022-9999-0000","Email":"mariko.kimura@northwind.co.jp"},
    {"No":7,"会社名":"合同会社デジタルクラフト","部署":"","役職":"Webデザイナー","氏名":"林大地","住所":"東京都台東区蔵前36-37-38","TEL":"03-2222-3333","Email":"daichi.hayashi@digitalcraft.jp"},
    {"No":8,"会社名":"株式会社サクラファーム","部署":"農業事業部","役職":"農場長","氏名":"斎藤和也","住所":"長野県長野市篠ノ井39-40","TEL":"026-4444-5555","Email":"kazuya.sato@sakurafarm.co.jp"},
    {"No":9,"会社名":"一般社団法人日本IT推進協会","部署":"事務局","役職":"事務局長","氏名":"山口恵美","住所":"東京都港区赤坂41-42-43","TEL":"03-6666-7777","Email":"emi.yamaguchi@japan-it.or.jp"},
    {"No":10,"会社名":"株式会社リバーサイドホテル","部署":"フロント部","役職":"支配人","氏名":"清水翔太","住所":"静岡県熱海市銀座町44-45","TEL":"0557-8888-9999","Email":"shota.shimizu@riverside-hotel.co.jp"},
    {"No":11,"会社名":"有限会社ムーンライト出版","部署":"編集部","役職":"編集長","氏名":"藤田奈々","住所":"東京都新宿区神楽坂46-47","TEL":"03-0000-1111","Email":"nana.fujita@moonlight-pub.jp"},
    {"No":12,"会社名":"合同会社テクノブリッジ","部署":"開発部","役職":"エンジニア","氏名":"佐藤美咲","住所":"大阪府大阪市北区梅田4-5-6","TEL":"06-2345-6789","Email":"misaki.sato@technobridge.jp"},
    {"No":13,"会社名":"株式会社グリーンフォレスト","部署":"総務部","役職":"課長","氏名":"鈴木健一","住所":"愛知県名古屋市中区栄7-8-9","TEL":"052-346-7890","Email":"kenichi.suzuki@greenforest.co.jp"},
    {"No":14,"会社名":"有限会社ブルースカイ","部署":"著・企画部","役職":"主任","氏名":"田中花子","住所":"福岡県福岡市博多区中洲10-11","TEL":"092-4567-8901","Email":"hanako.tanaka@bluesky-llc.jp"},
    {"No":15,"会社名":"株式会社サンライズ電機","部署":"技術部","役職":"係長","氏名":"高橋誠","住所":"北海道札幌市中央区大通12-13","TEL":"011-5678-9012","Email":"makoto.takahashi@sunrise-denki.co.jp"},
    {"No":16,"会社名":"NPO法人みらい教育","部署":"事務局","役職":"局長","氏名":"渡辺裕子","住所":"京都府京都市左京区下鴨14-15","TEL":"075-6789-0123","Email":"yuko.watanabe@mirai-edu.org"},
    {"No":17,"会社名":"株式会社オーシャンフーズ","部署":"品質管理部","役職":"マネージャー","氏名":"伊藤大輔","住所":"神奈川県横浜市西区みなとみらい16-17","TEL":"045-7890-1234","Email":"daisuke.ito@oceanfoods.co.jp"},
    {"No":18,"会社名":"合同会社クラウドネクスト","部署":"","役職":"CTO","氏名":"小林拓也","住所":"東京都渋谷区神宮前18-19-20","TEL":"03-8901-2345","Email":"takuya.kobayashi@cloudnext.io"},
    {"No":19,"会社名":"株式会社和風堂","部署":"販売部","役職":"店長","氏名":"加藤さくら","住所":"奈良県奈良市三条町21-22","TEL":"0742-9012-3456","Email":"sakura.kato@wafudo.co.jp"},
    {"No":20,"会社名":"医療法人健康会","部署":"事務部","役職":"事務長","氏名":"吉田正明","住所":"広島県広島市南区松原23-24","TEL":"082-0123-4567","Email":"masaaki.yoshida@kenkoukai.or.jp"},
]

headers = ["No","会社名","部署","役職","氏名","住所","TEL","Email"]
output_path = "/home/user/my-project/名刺一覧.xlsx"

all_strings = []
string_index = {}

def get_si(s):
    s = str(s)
    if s not in string_index:
        string_index[s] = len(all_strings)
        all_strings.append(s)
    return string_index[s]

for h in headers:
    get_si(h)
for card in cards:
    for h in headers:
        get_si(str(card.get(h, "")))

def col_letter(n):
    letters = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        letters = chr(65 + r) + letters
    return letters

def build_sheet():
    rows_xml = []
    cells = ""
    for ci, h in enumerate(headers, 1):
        ref = f"{col_letter(ci)}1"
        si = get_si(h)
        cells += f'<c r="{ref}" t="s" s="1"><v>{si}</v></c>'
    rows_xml.append(f'<row r="1">{cells}</row>')
    for ri, card in enumerate(cards, 2):
        cells = ""
        for ci, h in enumerate(headers, 1):
            ref = f"{col_letter(ci)}{ri}"
            val = card.get(h, "")
            if h == "No":
                cells += f'<c r="{ref}" s="2"><v>{val}</v></c>'
            else:
                si = get_si(str(val))
                cells += f'<c r="{ref}" t="s" s="2"><v>{si}</v></c>'
        rows_xml.append(f'<row r="{ri}">{cells}</row>')
    col_widths = ""
    for i, w in enumerate([4,28,14,16,12,36,16,36], 1):
        col_widths += f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>{col_widths}</cols><sheetData>{"".join(rows_xml)}</sheetData></worksheet>'

def build_shared_strings():
    items = ""
    for s in all_strings:
        escaped = s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        items += f'<si><t xml:space="preserve">{escaped}</t></si>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(all_strings)}" uniqueCount="{len(all_strings)}">{items}</sst>'

styles_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF4472C4"/></fgColor></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FF000000"/></left><right style="thin"><color rgb="FF000000"/></right><top style="thin"><color rgb="FF000000"/></top><bottom style="thin"><color rgb="FF000000"/></bottom></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"><alignment vertical="center"/></xf></cellXfs></styleSheet>'

workbook_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="名刺一覧" sheetId="1" r:id="rId1"/></sheets></workbook>'
workbook_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
rels_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>'

sheet_xml = build_sheet()
shared_strings_xml = build_shared_strings()

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("[Content_Types].xml", content_types)
    zf.writestr("_rels/.rels", rels_xml)
    zf.writestr("xl/workbook.xml", workbook_xml)
    zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
    zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    zf.writestr("xl/sharedStrings.xml", shared_strings_xml)
    zf.writestr("xl/styles.xml", styles_xml)

print(f"完了: {output_path}")
print(f"サイズ: {os.path.getsize(output_path):,} bytes")
