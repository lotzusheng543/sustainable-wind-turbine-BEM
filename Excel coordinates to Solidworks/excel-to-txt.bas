Attribute VB_Name = "Module1"
Sub ExportDataToText()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim midRow As Long
    Dim i As Long, r As Long
    Dim filePath As String
    Dim fileNum As Integer
    Dim cellValue As String
    
    ' Loop through every sheet in the workbook
    For Each ws In ThisWorkbook.Worksheets
        
        ' 1. Define the last row of the coordinates
        lastRow = 200

        ' 2. Define the file path
        ' Change this path if you want it saved elsewhere
        filePath = "C:\xxx\xxx\" & ws.Name & "external_top.txt"
        fileNum = FreeFile
        
        ' 3. Create/Open the text file
        Open filePath For Output As #fileNum
        
        ' 4. Loop through the rows (1 to last row) and columns A to C
        'change the numbers if the columns are different
        
        For r = 1 To midRow
            cellValue = ws.Cells(r, 1).Text & vbTab & _
                        ws.Cells(r, 2).Text & vbTab & _
                        ws.Cells(r, 3).Text
            Print #fileNum, cellValue
        Next r
        ' Close the file for the current sheet
        Close #fileNum
        
    Next ws
    
    MsgBox "Export Complete! Files are in your Documents folder.", vbInformation
End Sub



