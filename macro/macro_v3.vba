Sub pdf_genereren()

    Dim projectDir As String, pythonExe As String
    Dim localOneDrive As String, marker As String
    Dim pos As Long

    projectDir = ThisWorkbook.Path
    
    ' 1. Handle OneDrive/SharePoint URL conversion
    If Left(projectDir, 4) = "http" Then
        localOneDrive = Environ("OneDrive")
        If localOneDrive = "" Then localOneDrive = Environ("OneDriveCommercial")
        
        If InStr(1, projectDir, "/personal/", vbTextCompare) > 0 Then marker = "/personal/" Else marker = "/sites/"
        
        If localOneDrive <> "" Then
            pos = InStr(InStr(1, projectDir, marker) + Len(marker), projectDir, "/")
            If pos > 0 Then
                ' Rebuild path, swap slashes, and fix spaces (%20)
                projectDir = localOneDrive & "\" & Replace(Replace(Mid(projectDir, pos + 1), "/", "\"), "%20", " ")
                
                ' Clean fix for the missing intermediate "\Documents\" folder bug
                With CreateObject("Scripting.FileSystemObject")
                    If Not .FolderExists(projectDir) Then
                        If .FolderExists(Replace(projectDir, "\Documents\", "\", , , vbTextCompare)) Then
                            projectDir = Replace(projectDir, "\Documents\", "\", , , vbTextCompare)
                        End If
                    End If
                End With
            End If
        End If
    End If

    ' 2. Dynamically locate Python
    On Error Resume Next
    pythonExe = Trim(CreateObject("WScript.Shell").exec("cmd.exe /c where python").StdOut.ReadLine)
    On Error GoTo 0
    If pythonExe = "" Then pythonExe = "python"

    ' 3. Format and execute the final command line
    Shell "cmd.exe /k ""cd /d """ & projectDir & """ && """ & pythonExe & """ main.py pdf " & _
          Range("B2").Value & " " & Replace(Range("B3").Value, ",", ".") & """", vbNormalFocus

End Sub
