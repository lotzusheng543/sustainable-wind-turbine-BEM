Attribute VB_Name = "Module3"
Dim swApp As SldWorks.SldWorks
Dim swModel As SldWorks.ModelDoc2
Dim boolstatus As Boolean

Sub main()
 
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc

    ' 1. Safety Checks
    If swModel Is Nothing Then
        MsgBox "Please open a Part document first.", vbCritical
        Exit Sub
    End If
    
    If swModel.GetType <> swDocPART Then
        MsgBox "This macro only works in Part documents.", vbCritical
        Exit Sub
    End If

    ' 2. Define your target directory
    Dim folderPath As String
    Dim fileName As String
    
    ' Ensure the path ends with a backslash \
    folderPath = "C:\xxx\xxx\" & "*.txt"

    ' 3. Find the first .txt file in that folder
    fileName = Dir(folderPath)

    ' 4. Loop through every file found
    If fileName = "" Then
        MsgBox "No .txt files found in: " & folderPath, vbExclamation
        Exit Sub
    End If

    Do While fileName <> ""
        ' Create the Curve Through XYZ Points using the full path
        boolstatus = swModel.InsertCurveFile(folderPath & fileName)
     
        If boolstatus Then
            ' Optional: Clear selection to prevent cluttering
            swModel.ClearSelection2 True
        Else
            Debug.Print "Failed to import: " & fileName
        End If
        
        ' Move to the next file in the folder
        fileName = Dir
    Loop

    ' Final View adjustment
    swModel.ViewZoomtofit2
    MsgBox "Import Complete!", vbInformation

End Sub
