[General]
SyntaxVersion=2
BeginHotkey=120
BeginHotkeyMod=0
PauseHotkey=80
PauseHotkeyMod=1
StopHotkey=121
StopHotkeyMod=0
RunOnce=1
EnableWindow=
MacroID=06b1f4a4-179e-4508-a5a5-47e6cf33bf0f
Description=DBDautoscript
Enable=1
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=2
QUI=
[Relative]
SetupOCXFile=
[Comment]
�˽ű���Դ���
��Ŀ��ַ��https://github.com/maskrs/DBD_AFK_TOOL

[Script]
/////////////////////////////////////////////
//                                         //
//�˽ű���Դ��ѣ���Ŀ��ַ��                 //
//https://github.com/maskrs/DBD_AFK_TOOL   //
//                                         //
/////////////////////////////////////////////


//Goto ����//����
//Call CheckTime()//��⵱ǰʱ��.1
Global i,jni,dxi,ejnX,ejnY,yjnX,yjnY,inX,inY,zy,xdi//������Ҫ�ı���
i = 0
jni = 0
dxi = 0
xdi = 0
//Rem ����
zy = MsgBox("�Ƿ�ʹ��������Ӫ��ѡ�񡮷���Ϊ����", 4, "ѡ����Ӫ")
NUM = InputBox("�����ֻ�����/�����������                                                                     ѡ�񵥶���ɫģʽ����0                                                                        'ȡ��'�˳�","ѡ��һ�ģʽ")
//���Ҵ�������(0)���߱���("DeadByDaylight  "),�����ҵ��ľ��Hwnd
Hwnd = Plugin.Window.Find(0, "DeadByDaylight  ")
//Call Plugin.Window.Show(Hwnd)
Call Plugin.Window.Top(Hwnd, 0)
Call Plugin.Window.Top(Hwnd, 1)
If   IsEmpty(NUM) = True Then
    ExitScript
End If
num = CInt(NUM)
If zy = 6 Then //�ж����������Ƿ񳬹����ֵ
    If num > 31 Then //��������ɫ����
        MessageBox ("���������������ű���")
        EndScript
    ElseIf num = 0 Then
        Goto  ƥ��
    End If
ElseIf zy = 7 Then
    If num > 29 Then //��������ɫ����
        MessageBox ("���������������ű���")
        EndScript
    ElseIf num = 0 Then
        Goto  ƥ��
    End If
End If 
Rem ѡ��
FindColorEx 105,873,178,149,"7F7F7F",0,0.9,intX,intY//���ͼ��Ұ�ɫ
If intX > 0 And intY > 0 Then 
    Delay 3000
    Call change()
Else 
    Call dx()//������
    If dxi = 1 Then 
        Goto ����  
    End If
    Goto ѡ��
End If
Rem ƥ��
//Call CheckTime()//�ٴμ�⵱ǰʱ��.2
//���Ѫ��,�Ƿ����ƥ�����
Call xd()
If xdi = 1 Then 
    If num = 0 Then 
        Delay 5000
    End If
    MoveTo 1, 1
    Delay 500
    LeftClick 1
    Delay 1000
    MoveTo 1758, 1003
    Delay 1000
    LeftClick 1
    Delay 500
    MoveTo 139, 689
    Delay 1500
    Call dx()//������
    If dxi = 1 Then 
        Goto ����  
    End If
    Delay 1500
    FindColor 292,978,341,1032,"7F7F7F",intX,intY//������½�����
    If intX > 0 And intY > 0 Then 
        Goto ƥ��
    End If
Else 
    Call dx()//������
    If dxi = 1 Then 
        Goto ����  
    End If
    Goto ƥ��
End If
Rem ׼��
//Rem ����
//�Ƿ���뷿��
FindColor 292,978,341,1032,"7F7F7F",intX,intY//������½�����
If intX > 0  And intY > 0  Then 
    Delay 3000
    MoveTo 1, 1
    Delay 1000
    LeftClick 1
    Delay 2000
    MoveTo 1758, 1003
    Delay 1000
    LeftClick 1
    Delay 500
    MoveTo 105, 660
    Delay 2000
    If zy = 6 Then //������ʾ
        KeyPress "Enter", 1
        Delay 500
        //        KeyPress "T", 1
        //        KeyPress "H", 1
        //        KeyPress "I", 1
        //        KeyPress "S", 1
        //        KeyPress "Space", 1
        //        KeyPress "I", 1
        //        KeyPress "S", 1
        //        KeyPress "Space", 1
        KeyDown 16, 1
        KeyPress 65, 1
        KeyUp 16, 1
        KeyDown 16, 1
        KeyPress 70, 1
        KeyUp 16, 1
        KeyDown 16, 1
        KeyPress 75, 1
        KeyUp 16, 1
        //        KeyPress "Space", 1
        //        KeyPress "S", 1
        //        KeyPress "C", 1
        //        KeyPress "R", 1
        //        KeyPress "I", 1
        //        KeyPress "P", 1
        //        KeyPress "T", 1
        //        KeyPress "Enter", 1
    End If
Else
    Call dx()//������
    If dxi = 1 Then 
        Goto ����  
    End If
    Goto ׼��
End If
Rem ����
//Rem ����
//�Ƿ���ּ���ͼ��
Call jn()
If jni = 1 Then
    Delay 3000
Else 
    FindColorEx 231,1,335,46,"84847D",0,0.9,intA,intB//��Ʒȼ�ս��棬�Է�������
    Call dx()
    If intA > 0 and intB > 0  Then 
        Goto ����
    ElseIf  dxi = 1 Then
        Goto ����
    End If
    Goto ����
End If
Rem ����
Call jn()
If jni = 1 Then 
    If zy = 6 Then 
        Call human()
        Goto ����
    ElseIf zy = 7 Then
        Call killer()
        Goto ����
    End If	
Else 
    Delay  2000
    Call dx()//�Ƿ����
    If dxi = 1 Then 
        Goto ����
    End If
    /*���Ѫ�㣬ȷ���Ծ�ȷʵ����*/
    Call xd()
    If xdi = 0 Then 
        Goto ����
    Else 
        Delay 5000
        MoveTo 200, 867
        Delay 1000
        LeftClick 1
        MoveTo 1736, 1010
        LeftClick 1
        Delay 1000
        LeftClick 1
        If num < 1  Then 
            Goto ƥ��
        ElseIf num > 0 Then
            Goto ѡ��
        End If
    End If
End If
Rem ����
Delay 2000
MoveTo 586, 679  //�������1
LeftClick 1
Delay 1000
MoveTo 570, 710  //�������2
LeftClick 1
Delay 1000
MoveTo 1335, 635 //�������3
LeftClick 1
Delay 1000
MoveTo 1430, 640 //�������4
LeftClick 1
Delay 1000
MoveTo 563,722 //�������5
LeftClick 1
Delay 2000
//���Ѫ��,�ж϶������
Call xd()
If xdi = 1 Then     //С��
    FindColorEx 292,978,341,1032,"7F7F7F",0,0.9,intX,intY//������½�����
    If intX > 0 And intY > 0 Then 
        Goto ƥ��
    End If
    MoveTo 1335, 635
    LeftClick 1
    Delay 1000
    MoveTo 1736, 1010
    LeftClick 1
    Delay 1000
    LeftClick 1
    Goto ƥ��
Else
    //����
    Rem ����
    Delay 1000
    LeftClick 1
    Delay 1000
    Call dx()/*������*/
    If dxi = 1 Then
        MoveTo 1335, 635  //�ؽ�
        LeftClick 1
        Delay 1000
        MoveTo 1335, 667  //�ؽ�������
        LeftClick 1
        Delay 1000
        LeftClick 1//�ؽ�
        Goto ����
    End If
    Delay 1000
    MoveTo 1453, 628  //����
    LeftClick 1
    Delay 1000
    MoveTo 1413, 992 //���ŵ��
    LeftClick 1
    Delay 1000
    MoveTo 1430, 744 //�˺�����
    LeftClick 1
    Delay 1000
    MoveTo 1631, 966//ת��ϵͳ
    LeftClick 1
    Delay 1000
    //Rem ����
    //ÿ�ռ����ж�
    FindColor 448,271,512,301,"FFFFFF",intX,intY
    If intX> 0 And intY> 0 Then
        MoveTo 483, 896
        LeftClick 1
        Delay 1000
    End If
    FindColorEx 504,935,569,997,"7F7F7F",2,0.9,intX,intY//�Ƿ��ؽ���ҳ���ж�
    If intX > 0 And intY > 0 Then 
        If zy = 6 Then 
            MoveTo 143, 261//�ص�����
            LeftClick 1
        ElseIf zy = 7 Then
            MoveTo 135, 133 //�ص�����
            LeftClick 1
        End If
    Else
        Goto ����
    End If
    Goto ƥ��
End If
Sub CheckTime()/*���ʱ��*/
    dim t
    t=lib.����.��ȡ����ʱ��_��ǿ��("www.taobao.com")//��ֵ��ǰ����ʱ�䵽����t
    d = Day(t)
    y = Month(t)
    n = Year(t)
    If y >= 11 And d >= 1 And n >= 2022 Then //2022��10��31�չ���
        MessageBox "��ʧЧ"
        ExitScript
    End If	
End Sub
Sub change()
    Dim ghX
    ghX = Array(405, 548, 703, 854, 404,548, 703, 854,404, 548, 703, 854,404,548, 703,854,404,548, 703,854,404,548, 703,854,404,549,709,858,384,556,715,882)/*�ĸ�һ�飨548~404����Ŀǰ32��������һ����ɫ������߸�֮ǰ��һ��*/
    Dim ghY
    ghy = Array(314, 323, 318, 302, 536,323, 318, 302,536, 323, 318, 302,536,323, 318,302,536,323, 318,302,536,323, 318,302,536,517,528,523,753,741,749,750)
    Delay 1000
    MoveTo 1, 1
    Delay 1000
    LeftClick 1
    Delay 1000
    MoveTo 141,109
    Delay 1000
    LeftClick 1
    Rem �ж�
    If i < num  Then
        moveX = ghX(i)
        moveY = ghY(i)
        Delay 1000
        MoveTo moveX, moveY
        Delay 3000
        LeftClick 1
        i = i + 1
    Else
        i = 0
        If num > 4 Then 
            MoveTo 522, 394
            Delay 1000
            MouseWheel 1
            Delay 1000
            MouseWheel 1
        End If
        Goto �ж�
    End If
End Sub
Function jn()/*��⼼���Ƿ����*/
    FindColorEx 1605, 780, 1855, 1021, "5E2450", 0, 0.9, intX, intY//��������
    FindColorEx 1605, 780, 1855, 1021, "0E3807", 0, 0.9, ejnX, ejnY//��������
    FindColorEx 1605, 780, 1855, 1021, "2E9EC3", 0, 0.9, yjnX, yjnY//һ������
    FindColor 125,948,142,967,"FEFEFE",jntX,jntY//��༼��ͼ�꣨ά����ר�ã�
    If intX > 0 or intY > 0 or ejnX > 0 Or ejnY > 0 or yjnX > 0 or yjnY > 0 or jntX > 0 or jntY > 0 Then 
        jni = 1
    Else 
        jni = 0
    End If
End Function
Function dx()/*�����ߣ�����ɫ��*/
    //    FindColor 1882, 412, 1901, 425, "44447C",  intX, intY
    //    FindColor 1869, 405, 1915, 431, "13132E", inX, inY
    XY = Plugin.Color.FindColorBlock(1882, 412, 1915, 425, "13132E", 5, 5, 0, 1)
    iZB = InStr(XY, "|")
    X = CLng(Left(XY, iZB - 1))
    Y = CLng(Right(XY, Len(XY) - iZB))
    If  X>0 or Y>0 Then
        dxi = 1
    Else 
        dxi = 0
    End If
End Function
Function xd()/*���Ѫ�㡢������Ƭ*/
    FindColorEx 1232,53,1371,94,"03A1EA",0,0.9,ajX,ajY//����ϸ��
    FindColorEx 1366,57,1507,93,"C08185",0,0.9,spX,spY//ӫ����Ƭ
    FindColorEx 1571,52,1607,92,"0C04BF",0,0.9,xdX,xdY//Ѫ��
    If ajX > 0 and ajY > 0 and spX > 0 and spY > 0 and xdX > 0 and xdY > 0 Then 
        xdi = 1
    Else
        xdi = 0
    End  If
End Function
Sub human()//���ද��
    KeyDownH "Shift", 1
    Call n1()
    KeyDown act1, 1
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 500
    LeftDown 1
    Delay 2000
    LeftUp 1
    KeyUp act1,1
    Call n1()
    KeyDown act1,1
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 500
    LeftDown 1
    Delay 2000
    LeftUp 1
    KeyUp act1,1
    Call n1()
    KeyDown act1,1
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 500
    LeftDown 1
    Delay 2000
    LeftUp 1
    KeyPress "Space", 1
    KeyUp act1, 1
    KeyUpH "Shift", 1
End Sub
Sub killer()//������
    KeyDown "Up", 1 /**/
    Delay 1000
    KeyUp "Up", 1   /*̧ͷ*/
    Call n1()
    KeyDown act1, 1/**/
    Delay 1500
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 300
    KeyUp act1, 1
    Call n1()
    KeyDown act1,1
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 300
    KeyUp act1, 1
    Call n1()
    KeyDown act1,1
    Call n2()
    KeyDown act2, 1
    Delay Lib.�㷨.������ִ�(3)
    KeyUp act2, 1
    Delay 300
    KeyUp act1, 1/*���嶯��*/
    Call n1()
    KeyDown act1, 1
    Call n2()
    KeyDown act2,1
    Delay 200
    KeyDown "Ctrl", 1/**/
    Delay 4000
    KeyUp "Ctrl", 1/*����*/
    KeyDown "Down", 1/**/
    Delay 400
    KeyUp "Down", 1/*��ͷʹ�ü���*/
    KeyUp act2,1
    KeyUp act1, 1
    Call n1()
    KeyDown act1, 1
    Call n2()
    KeyDown act2, 1    
    RightDown 1/**/
    Delay 3000  
    KeyPress "Ctrl", 1
    RightUp 1/*�Ҽ�����*/
    Delay 3000
    KeyUp act2, 1
    KeyUp act1,1
    Call n1()
    KeyDown act1, 1
    Call n2()
    KeyDown act2,1
    RightDown 1/**/
    Delay 2500
    LeftClick 20
    RightUp 1
    Delay 1500
    KeyPress "Ctrl", 1/*�Ҽ��������ʹ��*/
    Delay 1500
    KeyPress "Space", 1
    KeyUp act2, 1
    KeyUp act1, 1//�������� 
End Sub
Function n1()//����ƶ�
    n = Int((6 - 1 + 1) * Rnd + 1)
    If n = 1 or n = 5 or n = 6 Then
        act1 = "W"
    End If
    If n = 2 Then
        act1 = "A"
    End If
    If n = 3 Then
        act1 = "D"
    End If
    If n = 4 Then
        act1 = "S"
    End If
End Function
Function n2()//���ת��
    n = Int((2 - 1 + 1) * Rnd + 1)
    If n = 1 Then
        act2 = "Q"
    End If
    If n = 2 Then
        act2 = "E"
    End If
End Function
