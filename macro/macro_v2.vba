Sub pdf_genereren()

    Dim pythonExe As String
    Dim projectDir As String
    Dim evCount As String
    Dim cosPhi As String
    Dim cmd As String
    Dim wsh As Object
    Dim exec As Object
    Dim fso As Object

    ' 1. Get the directory of the current Excel file
    projectDir = ThisWorkbook.Path
    
    ' Universal fix for OneDrive/SharePoint HTTP URLs
    If Left(projectDir, 4) = "http" Then
        Dim localOneDrive As String
        localOneDrive = Environ("OneDrive")
        If localOneDrive = "" Then localOneDrive = Environ("OneDriveCommercial")
        
        Dim marker As String
        If InStr(1, projectDir, "/personal/", vbTextCompare) > 0 Then
            marker = "/personal/"
        ElseIf InStr(1, projectDir, "/sites/", vbTextCompare) > 0 Then
            marker = "/sites/"
        End If
        
        If marker <> "" And localOneDrive <> "" Then
            Dim pos As Long
            pos = InStr(1, projectDir, marker) + Len(marker)
            pos = InStr(pos, projectDir, "/")
            
            If pos > 0 Then
                Dim relativePart As String
                relativePart = Mid(projectDir, pos + 1)
                relativePart = Replace(relativePart, "/", "\")
                relativePart = Replace(relativePart, "%20", " ")
                
                ' Construct primary guess path
                projectDir = localOneDrive & "\" & relativePart
                
                ' Smart OneDrive Sync Verification
                Set fso = CreateObject("Scripting.FileSystemObject")
                If Not fso.FolderExists(projectDir) Then
                    ' If the path fails, check if removing intermediate "\Documents\" fixes it
                    Dim structuralFix As String
                    structuralFix = Replace(projectDir, "\Documents\", "\", , , vbTextCompare)
                    
                    If fso.FolderExists(structuralFix) Then
                        projectDir = structuralFix
                    End If
                End If
            End If
        End If
    End If

    ' 2. Dynamically find the active Python executable
    Set wsh = CreateObject("WScript.Shell")
    On Error Resume Next
    Set exec = wsh.exec("cmd.exe /c where python")
    pythonExe = Trim(exec.StdOut.ReadLine)
    On Error GoTo 0

    If pythonExe = "" Then
        pythonExe = "python"
    End If

    ' 3. Get values from the sheet and fix decimal commas
    evCount = Range("B2").Value
    cosPhi = Range("B3").Value
    cosPhi = Replace(cosPhi, ",", ".")

    ' 4. Final execution string
    cmd = "cmd.exe /k ""cd /d """ & projectDir & """ && """ & pythonExe & """ main.py pdf " & evCount & " " & cosPhi & """"

    ' Run it!
    Shell cmd, vbNormalFocus

End Sub
