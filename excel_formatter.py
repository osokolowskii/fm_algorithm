from openpyxl import load_workbook
from openpyxl.styles import Border, Side

def add_borders_to_excel(filename):
    # Wczytanie pliku Excela
    wb = load_workbook(filename)

    # Wybór aktywnego arkusza
    ws = wb.active

    # Utworzenie grubego obramowania
    thick_right_border = Border(right=Side(style='thick'))

    # Dodanie obramowania do komórek w kolumnach, które są wielokrotnościami trzech
    for col_idx, col in enumerate(ws.columns, start=1):
        if col_idx % 3 == 0:  # Jeśli kolumna jest wielokrotnością trzech
            for cell in col:
                cell.border = thick_right_border

    # Dostosowanie szerokości kolumn do zawartości
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

    # Zapisanie zmian
    wb.save(filename)

# Użycie funkcji
add_borders_to_excel('role_rankings.xlsx')