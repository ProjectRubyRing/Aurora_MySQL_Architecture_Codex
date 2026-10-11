"""Open read-only in installed Excel and export representative sheets for visual review."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pymupdf as fitz
import pythoncom
import win32com.client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation'
OUT.mkdir(exist_ok=True)
WORKBOOK = ROOT / 'deliverables' / 'Aurora_GlobalDatabase_Design_Assessment_2026-10-11.xlsx'


def main():
    report = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'samples': []}
    pythoncom.CoInitialize()
    app = None
    book = None
    try:
        print('Activating installed Excel through COM...', flush=True)
        app = win32com.client.DispatchEx('Excel.Application')
        app.Visible = False
        app.DisplayAlerts = False
        app.EnableEvents = False
        app.AskToUpdateLinks = False
        app.AutomationSecurity = 3
        print('Opening the workbook read-only...', flush=True)
        book = app.Workbooks.Open(str(WORKBOOK), UpdateLinks=0, ReadOnly=True)
        report['excel_version'] = str(app.Version)
        report['opened_read_only'] = bool(book.ReadOnly)
        report['sheets'] = int(book.Worksheets.Count)
        app.CalculateFull()
        calculator = book.Worksheets('15_接続数試算')
        report['recalculated_values'] = [calculator.Cells(r, 3).Value for r in range(19, 25)]
        original = calculator.Range('C11').Value
        calculator.Range('C11').Value = 50
        app.CalculateFull()
        report['changed_input_recalculation'] = {'containers': 50, 'connection_candidates': calculator.Range('C19').Value,
                                                'headroom': calculator.Range('C21').Value, 'result': calculator.Range('C24').Value}
        calculator.Range('C11').Value = original
        app.CalculateFull()
        samples = [('00_はじめに', 'cover', None), ('02_構成図', 'architecture', None),
                   ('07_Proxy設定', 'proxy_sample', 'A1:F16'), ('10_タイムアウト', 'timeout_sample', 'A1:H17'),
                   ('20_クラスタ既定', 'parameter_sample', 'A65:M75'), ('15_接続数試算', 'capacity', None)]
        for sheet_name, stem, print_area in samples:
            sheet = book.Worksheets(sheet_name)
            if print_area:
                sheet.PageSetup.PrintArea = print_area
                sheet.PageSetup.FitToPagesWide = 1
                sheet.PageSetup.FitToPagesTall = 1
            pdf = OUT / f'{stem}.pdf'
            sheet.ExportAsFixedFormat(0, str(pdf))
            with fitz.open(pdf) as doc:
                item = {'sheet': sheet_name, 'pdf': pdf.name, 'pages': len(doc),
                        'extracted_characters': sum(len(p.get_text()) for p in doc),
                        'fonts': sorted({f[3] for p in doc for f in p.get_fonts()})}
                for index, page in enumerate(doc):
                    png = OUT / f'{stem}_{index+1}.png'
                    page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False).save(png)
                report['samples'].append(item)
        report['result'] = 'PASS'
    except Exception as failure:
        report['result'] = 'FAIL'
        report['error'] = f'{type(failure).__name__}: {failure}'
    finally:
        if book is not None:
            book.Close(SaveChanges=False)
        if app is not None:
            app.Quit()
        pythoncom.CoUninitialize()
        (OUT / 'excel_render_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
