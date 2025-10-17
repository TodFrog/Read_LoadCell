<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Form1
    Inherits System.Windows.Forms.Form

    'Form은 Dispose를 재정의하여 구성 요소 목록을 정리합니다.
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Windows Form 디자이너에 필요합니다.
    Private components As System.ComponentModel.IContainer

    '참고: 다음 프로시저는 Windows Form 디자이너에 필요합니다.
    '수정하려면 Windows Form 디자이너를 사용하십시오.  
    '코드 편집기에서는 수정하지 마세요.
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Me.CbBox_com_port = New System.Windows.Forms.ComboBox()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Btn_comm_set = New System.Windows.Forms.Button()
        Me.SerialPort1 = New System.IO.Ports.SerialPort(Me.components)
        Me.GroupBox1 = New System.Windows.Forms.GroupBox()
        Me.Btn_comm_stop = New System.Windows.Forms.Button()
        Me.Rtb_rx_data = New System.Windows.Forms.RichTextBox()
        Me.Label19 = New System.Windows.Forms.Label()
        Me.Timer1 = New System.Windows.Forms.Timer(Me.components)
        Me.Label20 = New System.Windows.Forms.Label()
        Me.Rtb_tx_data = New System.Windows.Forms.RichTextBox()
        Me.GroupBox2 = New System.Windows.Forms.GroupBox()
        Me.GroupBox7 = New System.Windows.Forms.GroupBox()
        Me.ComboBox_kind = New System.Windows.Forms.ComboBox()
        Me.ComboBox_down_range = New System.Windows.Forms.ComboBox()
        Me.ComboBox_zero_range = New System.Windows.Forms.ComboBox()
        Me.ComboBox_division = New System.Windows.Forms.ComboBox()
        Me.ComboBox_max_weight = New System.Windows.Forms.ComboBox()
        Me.Button_param = New System.Windows.Forms.Button()
        Me.Label7 = New System.Windows.Forms.Label()
        Me.Label6 = New System.Windows.Forms.Label()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.Label4 = New System.Windows.Forms.Label()
        Me.Label5 = New System.Windows.Forms.Label()
        Me.GroupBox6 = New System.Windows.Forms.GroupBox()
        Me.RButton_cal = New System.Windows.Forms.RadioButton()
        Me.RButton_ok = New System.Windows.Forms.RadioButton()
        Me.RButton_error = New System.Windows.Forms.RadioButton()
        Me.RButton_overload = New System.Windows.Forms.RadioButton()
        Me.RButton_err_zero = New System.Windows.Forms.RadioButton()
        Me.GroupBox5 = New System.Windows.Forms.GroupBox()
        Me.Label_adr = New System.Windows.Forms.Label()
        Me.Label29 = New System.Windows.Forms.Label()
        Me.GroupBox4 = New System.Windows.Forms.GroupBox()
        Me.Label_id3 = New System.Windows.Forms.Label()
        Me.Label_id2 = New System.Windows.Forms.Label()
        Me.Label_id1 = New System.Windows.Forms.Label()
        Me.Label_id0 = New System.Windows.Forms.Label()
        Me.Label21 = New System.Windows.Forms.Label()
        Me.Label18 = New System.Windows.Forms.Label()
        Me.Label17 = New System.Windows.Forms.Label()
        Me.Label14 = New System.Windows.Forms.Label()
        Me.Label16 = New System.Windows.Forms.Label()
        Me.GroupBox3 = New System.Windows.Forms.GroupBox()
        Me.Labe_ad_value = New System.Windows.Forms.Label()
        Me.Label12 = New System.Windows.Forms.Label()
        Me.Label_down_zero = New System.Windows.Forms.Label()
        Me.Label_kind = New System.Windows.Forms.Label()
        Me.Label_range_zero = New System.Windows.Forms.Label()
        Me.Label_division = New System.Windows.Forms.Label()
        Me.Label_max_weight = New System.Windows.Forms.Label()
        Me.Label15 = New System.Windows.Forms.Label()
        Me.Label13 = New System.Windows.Forms.Label()
        Me.Label11 = New System.Windows.Forms.Label()
        Me.Label10 = New System.Windows.Forms.Label()
        Me.Label8 = New System.Windows.Forms.Label()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.TextBox_weight = New System.Windows.Forms.TextBox()
        Me.ComboBox_adr = New System.Windows.Forms.ComboBox()
        Me.LC1Button_adr_ch = New System.Windows.Forms.Button()
        Me.Button_read_id = New System.Windows.Forms.Button()
        Me.Button_zero = New System.Windows.Forms.Button()
        Me.Button_weight = New System.Windows.Forms.Button()
        Me.Button_read_param = New System.Windows.Forms.Button()
        Me.GroupBox1.SuspendLayout()
        Me.GroupBox2.SuspendLayout()
        Me.GroupBox7.SuspendLayout()
        Me.GroupBox6.SuspendLayout()
        Me.GroupBox5.SuspendLayout()
        Me.GroupBox4.SuspendLayout()
        Me.GroupBox3.SuspendLayout()
        Me.SuspendLayout()
        '
        'CbBox_com_port
        '
        Me.CbBox_com_port.FormattingEnabled = True
        Me.CbBox_com_port.Location = New System.Drawing.Point(6, 20)
        Me.CbBox_com_port.Name = "CbBox_com_port"
        Me.CbBox_com_port.Size = New System.Drawing.Size(68, 20)
        Me.CbBox_com_port.TabIndex = 0
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Location = New System.Drawing.Point(80, 28)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(53, 12)
        Me.Label1.TabIndex = 1
        Me.Label1.Text = "통신포트"
        '
        'Btn_comm_set
        '
        Me.Btn_comm_set.Location = New System.Drawing.Point(70, 53)
        Me.Btn_comm_set.Name = "Btn_comm_set"
        Me.Btn_comm_set.Size = New System.Drawing.Size(56, 27)
        Me.Btn_comm_set.TabIndex = 6
        Me.Btn_comm_set.Text = "열기"
        Me.Btn_comm_set.UseVisualStyleBackColor = True
        '
        'GroupBox1
        '
        Me.GroupBox1.Controls.Add(Me.Btn_comm_stop)
        Me.GroupBox1.Controls.Add(Me.CbBox_com_port)
        Me.GroupBox1.Controls.Add(Me.Btn_comm_set)
        Me.GroupBox1.Controls.Add(Me.Label1)
        Me.GroupBox1.Location = New System.Drawing.Point(12, 15)
        Me.GroupBox1.Name = "GroupBox1"
        Me.GroupBox1.Size = New System.Drawing.Size(135, 87)
        Me.GroupBox1.TabIndex = 7
        Me.GroupBox1.TabStop = False
        Me.GroupBox1.Text = "통신설정"
        '
        'Btn_comm_stop
        '
        Me.Btn_comm_stop.Location = New System.Drawing.Point(8, 55)
        Me.Btn_comm_stop.Name = "Btn_comm_stop"
        Me.Btn_comm_stop.Size = New System.Drawing.Size(53, 24)
        Me.Btn_comm_stop.TabIndex = 7
        Me.Btn_comm_stop.Text = "닫기"
        Me.Btn_comm_stop.UseVisualStyleBackColor = True
        '
        'Rtb_rx_data
        '
        Me.Rtb_rx_data.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.Rtb_rx_data.ForeColor = System.Drawing.SystemColors.MenuHighlight
        Me.Rtb_rx_data.Location = New System.Drawing.Point(291, 372)
        Me.Rtb_rx_data.Name = "Rtb_rx_data"
        Me.Rtb_rx_data.Size = New System.Drawing.Size(475, 66)
        Me.Rtb_rx_data.TabIndex = 19
        Me.Rtb_rx_data.Text = ""
        '
        'Label19
        '
        Me.Label19.AutoSize = True
        Me.Label19.Location = New System.Drawing.Point(217, 375)
        Me.Label19.Name = "Label19"
        Me.Label19.Size = New System.Drawing.Size(65, 12)
        Me.Label19.TabIndex = 20
        Me.Label19.Text = "수신데이터"
        '
        'Timer1
        '
        '
        'Label20
        '
        Me.Label20.AutoSize = True
        Me.Label20.Location = New System.Drawing.Point(217, 338)
        Me.Label20.Name = "Label20"
        Me.Label20.Size = New System.Drawing.Size(65, 12)
        Me.Label20.TabIndex = 21
        Me.Label20.Text = "송신데이터"
        '
        'Rtb_tx_data
        '
        Me.Rtb_tx_data.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.Rtb_tx_data.Location = New System.Drawing.Point(291, 332)
        Me.Rtb_tx_data.Name = "Rtb_tx_data"
        Me.Rtb_tx_data.Size = New System.Drawing.Size(478, 25)
        Me.Rtb_tx_data.TabIndex = 22
        Me.Rtb_tx_data.Text = ""
        '
        'GroupBox2
        '
        Me.GroupBox2.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
        Me.GroupBox2.Controls.Add(Me.GroupBox7)
        Me.GroupBox2.Controls.Add(Me.GroupBox6)
        Me.GroupBox2.Controls.Add(Me.GroupBox5)
        Me.GroupBox2.Controls.Add(Me.GroupBox4)
        Me.GroupBox2.Controls.Add(Me.GroupBox3)
        Me.GroupBox2.Controls.Add(Me.Label2)
        Me.GroupBox2.Controls.Add(Me.TextBox_weight)
        Me.GroupBox2.Controls.Add(Me.ComboBox_adr)
        Me.GroupBox2.Controls.Add(Me.LC1Button_adr_ch)
        Me.GroupBox2.Font = New System.Drawing.Font("굴림", 20.0!)
        Me.GroupBox2.ForeColor = System.Drawing.SystemColors.MenuHighlight
        Me.GroupBox2.Location = New System.Drawing.Point(153, 15)
        Me.GroupBox2.Name = "GroupBox2"
        Me.GroupBox2.Size = New System.Drawing.Size(635, 311)
        Me.GroupBox2.TabIndex = 23
        Me.GroupBox2.TabStop = False
        Me.GroupBox2.Text = "로드셀1"
        '
        'GroupBox7
        '
        Me.GroupBox7.Controls.Add(Me.ComboBox_kind)
        Me.GroupBox7.Controls.Add(Me.ComboBox_down_range)
        Me.GroupBox7.Controls.Add(Me.ComboBox_zero_range)
        Me.GroupBox7.Controls.Add(Me.ComboBox_division)
        Me.GroupBox7.Controls.Add(Me.ComboBox_max_weight)
        Me.GroupBox7.Controls.Add(Me.Button_param)
        Me.GroupBox7.Controls.Add(Me.Label7)
        Me.GroupBox7.Controls.Add(Me.Label6)
        Me.GroupBox7.Controls.Add(Me.Label3)
        Me.GroupBox7.Controls.Add(Me.Label4)
        Me.GroupBox7.Controls.Add(Me.Label5)
        Me.GroupBox7.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.GroupBox7.Location = New System.Drawing.Point(235, 28)
        Me.GroupBox7.Name = "GroupBox7"
        Me.GroupBox7.Size = New System.Drawing.Size(268, 179)
        Me.GroupBox7.TabIndex = 49
        Me.GroupBox7.TabStop = False
        Me.GroupBox7.Text = "파라미터 변경"
        '
        'ComboBox_kind
        '
        Me.ComboBox_kind.Cursor = System.Windows.Forms.Cursors.AppStarting
        Me.ComboBox_kind.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.ComboBox_kind.ForeColor = System.Drawing.Color.Brown
        Me.ComboBox_kind.FormattingEnabled = True
        Me.ComboBox_kind.Location = New System.Drawing.Point(69, 118)
        Me.ComboBox_kind.Name = "ComboBox_kind"
        Me.ComboBox_kind.Size = New System.Drawing.Size(82, 20)
        Me.ComboBox_kind.TabIndex = 54
        '
        'ComboBox_down_range
        '
        Me.ComboBox_down_range.Cursor = System.Windows.Forms.Cursors.AppStarting
        Me.ComboBox_down_range.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.ComboBox_down_range.ForeColor = System.Drawing.Color.Brown
        Me.ComboBox_down_range.FormattingEnabled = True
        Me.ComboBox_down_range.Location = New System.Drawing.Point(108, 92)
        Me.ComboBox_down_range.Name = "ComboBox_down_range"
        Me.ComboBox_down_range.Size = New System.Drawing.Size(154, 20)
        Me.ComboBox_down_range.TabIndex = 53
        '
        'ComboBox_zero_range
        '
        Me.ComboBox_zero_range.Cursor = System.Windows.Forms.Cursors.AppStarting
        Me.ComboBox_zero_range.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.ComboBox_zero_range.ForeColor = System.Drawing.Color.Brown
        Me.ComboBox_zero_range.FormattingEnabled = True
        Me.ComboBox_zero_range.Location = New System.Drawing.Point(107, 68)
        Me.ComboBox_zero_range.Name = "ComboBox_zero_range"
        Me.ComboBox_zero_range.Size = New System.Drawing.Size(155, 20)
        Me.ComboBox_zero_range.TabIndex = 52
        '
        'ComboBox_division
        '
        Me.ComboBox_division.Cursor = System.Windows.Forms.Cursors.AppStarting
        Me.ComboBox_division.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.ComboBox_division.ForeColor = System.Drawing.Color.Brown
        Me.ComboBox_division.FormattingEnabled = True
        Me.ComboBox_division.Location = New System.Drawing.Point(108, 43)
        Me.ComboBox_division.Name = "ComboBox_division"
        Me.ComboBox_division.Size = New System.Drawing.Size(154, 20)
        Me.ComboBox_division.TabIndex = 51
        '
        'ComboBox_max_weight
        '
        Me.ComboBox_max_weight.Cursor = System.Windows.Forms.Cursors.AppStarting
        Me.ComboBox_max_weight.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.ComboBox_max_weight.ForeColor = System.Drawing.Color.Brown
        Me.ComboBox_max_weight.FormattingEnabled = True
        Me.ComboBox_max_weight.Location = New System.Drawing.Point(108, 19)
        Me.ComboBox_max_weight.Name = "ComboBox_max_weight"
        Me.ComboBox_max_weight.Size = New System.Drawing.Size(154, 20)
        Me.ComboBox_max_weight.TabIndex = 50
        '
        'Button_param
        '
        Me.Button_param.Font = New System.Drawing.Font("굴림", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(129, Byte))
        Me.Button_param.ForeColor = System.Drawing.Color.Maroon
        Me.Button_param.Location = New System.Drawing.Point(14, 142)
        Me.Button_param.Name = "Button_param"
        Me.Button_param.Size = New System.Drawing.Size(75, 30)
        Me.Button_param.TabIndex = 49
        Me.Button_param.Text = "변경"
        Me.Button_param.UseVisualStyleBackColor = True
        '
        'Label7
        '
        Me.Label7.AutoSize = True
        Me.Label7.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label7.ForeColor = System.Drawing.SystemColors.Desktop
        Me.Label7.Location = New System.Drawing.Point(10, 120)
        Me.Label7.Name = "Label7"
        Me.Label7.Size = New System.Drawing.Size(53, 12)
        Me.Label7.TabIndex = 48
        Me.Label7.Text = "저울종류"
        '
        'Label6
        '
        Me.Label6.AutoSize = True
        Me.Label6.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label6.ForeColor = System.Drawing.SystemColors.Desktop
        Me.Label6.Location = New System.Drawing.Point(9, 97)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(97, 12)
        Me.Label6.TabIndex = 47
        Me.Label6.Text = "안착영점범위(%)"
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label3.ForeColor = System.Drawing.SystemColors.Desktop
        Me.Label3.Location = New System.Drawing.Point(8, 24)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(88, 12)
        Me.Label3.TabIndex = 46
        Me.Label3.Text = "최대중량값(kg)"
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label4.ForeColor = System.Drawing.SystemColors.Desktop
        Me.Label4.Location = New System.Drawing.Point(8, 47)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(41, 12)
        Me.Label4.TabIndex = 45
        Me.Label4.Text = "분해도"
        '
        'Label5
        '
        Me.Label5.AutoSize = True
        Me.Label5.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label5.ForeColor = System.Drawing.SystemColors.Desktop
        Me.Label5.Location = New System.Drawing.Point(8, 71)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(73, 12)
        Me.Label5.TabIndex = 44
        Me.Label5.Text = "영점범위(%)"
        '
        'GroupBox6
        '
        Me.GroupBox6.BackColor = System.Drawing.SystemColors.ControlDark
        Me.GroupBox6.Controls.Add(Me.RButton_cal)
        Me.GroupBox6.Controls.Add(Me.RButton_ok)
        Me.GroupBox6.Controls.Add(Me.RButton_error)
        Me.GroupBox6.Controls.Add(Me.RButton_overload)
        Me.GroupBox6.Controls.Add(Me.RButton_err_zero)
        Me.GroupBox6.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.GroupBox6.ForeColor = System.Drawing.SystemColors.HotTrack
        Me.GroupBox6.Location = New System.Drawing.Point(509, 60)
        Me.GroupBox6.Name = "GroupBox6"
        Me.GroupBox6.Size = New System.Drawing.Size(117, 148)
        Me.GroupBox6.TabIndex = 48
        Me.GroupBox6.TabStop = False
        Me.GroupBox6.Text = "상태"
        '
        'RButton_cal
        '
        Me.RButton_cal.AutoSize = True
        Me.RButton_cal.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.RButton_cal.ForeColor = System.Drawing.SystemColors.InfoText
        Me.RButton_cal.Location = New System.Drawing.Point(6, 128)
        Me.RButton_cal.Name = "RButton_cal"
        Me.RButton_cal.Size = New System.Drawing.Size(85, 19)
        Me.RButton_cal.TabIndex = 36
        Me.RButton_cal.TabStop = True
        Me.RButton_cal.Text = "조정필요"
        Me.RButton_cal.UseVisualStyleBackColor = True
        '
        'RButton_ok
        '
        Me.RButton_ok.AutoSize = True
        Me.RButton_ok.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.RButton_ok.ForeColor = System.Drawing.SystemColors.InfoText
        Me.RButton_ok.Location = New System.Drawing.Point(7, 23)
        Me.RButton_ok.Name = "RButton_ok"
        Me.RButton_ok.Size = New System.Drawing.Size(55, 19)
        Me.RButton_ok.TabIndex = 34
        Me.RButton_ok.TabStop = True
        Me.RButton_ok.Text = "정상"
        Me.RButton_ok.UseVisualStyleBackColor = True
        '
        'RButton_error
        '
        Me.RButton_error.AutoSize = True
        Me.RButton_error.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.RButton_error.ForeColor = System.Drawing.SystemColors.InfoText
        Me.RButton_error.Location = New System.Drawing.Point(7, 48)
        Me.RButton_error.Name = "RButton_error"
        Me.RButton_error.Size = New System.Drawing.Size(55, 19)
        Me.RButton_error.TabIndex = 35
        Me.RButton_error.TabStop = True
        Me.RButton_error.Text = "에러"
        Me.RButton_error.UseVisualStyleBackColor = True
        '
        'RButton_overload
        '
        Me.RButton_overload.AutoSize = True
        Me.RButton_overload.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.RButton_overload.ForeColor = System.Drawing.SystemColors.InfoText
        Me.RButton_overload.Location = New System.Drawing.Point(7, 73)
        Me.RButton_overload.Name = "RButton_overload"
        Me.RButton_overload.Size = New System.Drawing.Size(70, 19)
        Me.RButton_overload.TabIndex = 36
        Me.RButton_overload.TabStop = True
        Me.RButton_overload.Text = "과중량"
        Me.RButton_overload.UseVisualStyleBackColor = True
        '
        'RButton_err_zero
        '
        Me.RButton_err_zero.AutoSize = True
        Me.RButton_err_zero.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.RButton_err_zero.ForeColor = System.Drawing.SystemColors.InfoText
        Me.RButton_err_zero.Location = New System.Drawing.Point(6, 98)
        Me.RButton_err_zero.Name = "RButton_err_zero"
        Me.RButton_err_zero.Size = New System.Drawing.Size(100, 19)
        Me.RButton_err_zero.TabIndex = 37
        Me.RButton_err_zero.TabStop = True
        Me.RButton_err_zero.Text = "영점조정됨"
        Me.RButton_err_zero.UseVisualStyleBackColor = True
        '
        'GroupBox5
        '
        Me.GroupBox5.BackColor = System.Drawing.SystemColors.ControlDark
        Me.GroupBox5.Controls.Add(Me.Label_adr)
        Me.GroupBox5.Controls.Add(Me.Label29)
        Me.GroupBox5.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.GroupBox5.ForeColor = System.Drawing.SystemColors.HotTrack
        Me.GroupBox5.Location = New System.Drawing.Point(437, 217)
        Me.GroupBox5.Name = "GroupBox5"
        Me.GroupBox5.Size = New System.Drawing.Size(86, 79)
        Me.GroupBox5.TabIndex = 47
        Me.GroupBox5.TabStop = False
        Me.GroupBox5.Text = "주소(adr)"
        '
        'Label_adr
        '
        Me.Label_adr.AutoSize = True
        Me.Label_adr.Font = New System.Drawing.Font("굴림", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(129, Byte))
        Me.Label_adr.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_adr.Location = New System.Drawing.Point(16, 31)
        Me.Label_adr.Name = "Label_adr"
        Me.Label_adr.Size = New System.Drawing.Size(53, 35)
        Me.Label_adr.TabIndex = 56
        Me.Label_adr.Text = "xx"
        '
        'Label29
        '
        Me.Label29.AutoSize = True
        Me.Label29.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label29.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label29.Location = New System.Drawing.Point(232, 19)
        Me.Label29.Name = "Label29"
        Me.Label29.Size = New System.Drawing.Size(19, 12)
        Me.Label29.TabIndex = 49
        Me.Label29.Text = "xx"
        '
        'GroupBox4
        '
        Me.GroupBox4.BackColor = System.Drawing.SystemColors.ControlDark
        Me.GroupBox4.Controls.Add(Me.Label_id3)
        Me.GroupBox4.Controls.Add(Me.Label_id2)
        Me.GroupBox4.Controls.Add(Me.Label_id1)
        Me.GroupBox4.Controls.Add(Me.Label_id0)
        Me.GroupBox4.Controls.Add(Me.Label21)
        Me.GroupBox4.Controls.Add(Me.Label18)
        Me.GroupBox4.Controls.Add(Me.Label17)
        Me.GroupBox4.Controls.Add(Me.Label14)
        Me.GroupBox4.Controls.Add(Me.Label16)
        Me.GroupBox4.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.GroupBox4.ForeColor = System.Drawing.SystemColors.HotTrack
        Me.GroupBox4.Location = New System.Drawing.Point(343, 218)
        Me.GroupBox4.Name = "GroupBox4"
        Me.GroupBox4.Size = New System.Drawing.Size(86, 79)
        Me.GroupBox4.TabIndex = 46
        Me.GroupBox4.TabStop = False
        Me.GroupBox4.Text = "고유id"
        '
        'Label_id3
        '
        Me.Label_id3.AutoSize = True
        Me.Label_id3.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_id3.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_id3.Location = New System.Drawing.Point(34, 64)
        Me.Label_id3.Name = "Label_id3"
        Me.Label_id3.Size = New System.Drawing.Size(19, 12)
        Me.Label_id3.TabIndex = 57
        Me.Label_id3.Text = "xx"
        '
        'Label_id2
        '
        Me.Label_id2.AutoSize = True
        Me.Label_id2.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_id2.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_id2.Location = New System.Drawing.Point(34, 49)
        Me.Label_id2.Name = "Label_id2"
        Me.Label_id2.Size = New System.Drawing.Size(19, 12)
        Me.Label_id2.TabIndex = 56
        Me.Label_id2.Text = "xx"
        '
        'Label_id1
        '
        Me.Label_id1.AutoSize = True
        Me.Label_id1.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_id1.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_id1.Location = New System.Drawing.Point(34, 35)
        Me.Label_id1.Name = "Label_id1"
        Me.Label_id1.Size = New System.Drawing.Size(19, 12)
        Me.Label_id1.TabIndex = 55
        Me.Label_id1.Text = "xx"
        '
        'Label_id0
        '
        Me.Label_id0.AutoSize = True
        Me.Label_id0.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_id0.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_id0.Location = New System.Drawing.Point(34, 20)
        Me.Label_id0.Name = "Label_id0"
        Me.Label_id0.Size = New System.Drawing.Size(19, 12)
        Me.Label_id0.TabIndex = 54
        Me.Label_id0.Text = "xx"
        '
        'Label21
        '
        Me.Label21.AutoSize = True
        Me.Label21.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label21.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label21.Location = New System.Drawing.Point(6, 61)
        Me.Label21.Name = "Label21"
        Me.Label21.Size = New System.Drawing.Size(21, 12)
        Me.Label21.TabIndex = 53
        Me.Label21.Text = "id3"
        '
        'Label18
        '
        Me.Label18.AutoSize = True
        Me.Label18.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label18.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label18.Location = New System.Drawing.Point(6, 47)
        Me.Label18.Name = "Label18"
        Me.Label18.Size = New System.Drawing.Size(21, 12)
        Me.Label18.TabIndex = 52
        Me.Label18.Text = "id2"
        '
        'Label17
        '
        Me.Label17.AutoSize = True
        Me.Label17.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label17.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label17.Location = New System.Drawing.Point(6, 35)
        Me.Label17.Name = "Label17"
        Me.Label17.Size = New System.Drawing.Size(21, 12)
        Me.Label17.TabIndex = 51
        Me.Label17.Text = "id1"
        '
        'Label14
        '
        Me.Label14.AutoSize = True
        Me.Label14.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label14.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label14.Location = New System.Drawing.Point(5, 21)
        Me.Label14.Name = "Label14"
        Me.Label14.Size = New System.Drawing.Size(21, 12)
        Me.Label14.TabIndex = 50
        Me.Label14.Text = "id0"
        '
        'Label16
        '
        Me.Label16.AutoSize = True
        Me.Label16.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label16.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label16.Location = New System.Drawing.Point(232, 19)
        Me.Label16.Name = "Label16"
        Me.Label16.Size = New System.Drawing.Size(19, 12)
        Me.Label16.TabIndex = 49
        Me.Label16.Text = "xx"
        '
        'GroupBox3
        '
        Me.GroupBox3.BackColor = System.Drawing.SystemColors.ControlDark
        Me.GroupBox3.Controls.Add(Me.Labe_ad_value)
        Me.GroupBox3.Controls.Add(Me.Label12)
        Me.GroupBox3.Controls.Add(Me.Label_down_zero)
        Me.GroupBox3.Controls.Add(Me.Label_kind)
        Me.GroupBox3.Controls.Add(Me.Label_range_zero)
        Me.GroupBox3.Controls.Add(Me.Label_division)
        Me.GroupBox3.Controls.Add(Me.Label_max_weight)
        Me.GroupBox3.Controls.Add(Me.Label15)
        Me.GroupBox3.Controls.Add(Me.Label13)
        Me.GroupBox3.Controls.Add(Me.Label11)
        Me.GroupBox3.Controls.Add(Me.Label10)
        Me.GroupBox3.Controls.Add(Me.Label8)
        Me.GroupBox3.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.GroupBox3.ForeColor = System.Drawing.SystemColors.HotTrack
        Me.GroupBox3.Location = New System.Drawing.Point(9, 218)
        Me.GroupBox3.Name = "GroupBox3"
        Me.GroupBox3.Size = New System.Drawing.Size(327, 79)
        Me.GroupBox3.TabIndex = 42
        Me.GroupBox3.TabStop = False
        Me.GroupBox3.Text = "parameter"
        '
        'Labe_ad_value
        '
        Me.Labe_ad_value.AutoSize = True
        Me.Labe_ad_value.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Labe_ad_value.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Labe_ad_value.Location = New System.Drawing.Point(231, 37)
        Me.Labe_ad_value.Name = "Labe_ad_value"
        Me.Labe_ad_value.Size = New System.Drawing.Size(19, 12)
        Me.Labe_ad_value.TabIndex = 52
        Me.Labe_ad_value.Text = "xx"
        '
        'Label12
        '
        Me.Label12.AutoSize = True
        Me.Label12.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label12.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label12.Location = New System.Drawing.Point(172, 37)
        Me.Label12.Name = "Label12"
        Me.Label12.Size = New System.Drawing.Size(31, 12)
        Me.Label12.TabIndex = 51
        Me.Label12.Text = "ad값"
        '
        'Label_down_zero
        '
        Me.Label_down_zero.AutoSize = True
        Me.Label_down_zero.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_down_zero.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_down_zero.Location = New System.Drawing.Point(279, 61)
        Me.Label_down_zero.Name = "Label_down_zero"
        Me.Label_down_zero.Size = New System.Drawing.Size(19, 12)
        Me.Label_down_zero.TabIndex = 50
        Me.Label_down_zero.Text = "xx"
        '
        'Label_kind
        '
        Me.Label_kind.AutoSize = True
        Me.Label_kind.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_kind.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_kind.Location = New System.Drawing.Point(232, 19)
        Me.Label_kind.Name = "Label_kind"
        Me.Label_kind.Size = New System.Drawing.Size(19, 12)
        Me.Label_kind.TabIndex = 49
        Me.Label_kind.Text = "xx"
        '
        'Label_range_zero
        '
        Me.Label_range_zero.AutoSize = True
        Me.Label_range_zero.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_range_zero.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_range_zero.Location = New System.Drawing.Point(96, 61)
        Me.Label_range_zero.Name = "Label_range_zero"
        Me.Label_range_zero.Size = New System.Drawing.Size(19, 12)
        Me.Label_range_zero.TabIndex = 48
        Me.Label_range_zero.Text = "xx"
        '
        'Label_division
        '
        Me.Label_division.AutoSize = True
        Me.Label_division.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_division.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_division.Location = New System.Drawing.Point(96, 40)
        Me.Label_division.Name = "Label_division"
        Me.Label_division.Size = New System.Drawing.Size(19, 12)
        Me.Label_division.TabIndex = 47
        Me.Label_division.Text = "xx"
        '
        'Label_max_weight
        '
        Me.Label_max_weight.AutoSize = True
        Me.Label_max_weight.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label_max_weight.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label_max_weight.Location = New System.Drawing.Point(96, 19)
        Me.Label_max_weight.Name = "Label_max_weight"
        Me.Label_max_weight.Size = New System.Drawing.Size(19, 12)
        Me.Label_max_weight.TabIndex = 46
        Me.Label_max_weight.Text = "xx"
        '
        'Label15
        '
        Me.Label15.AutoSize = True
        Me.Label15.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label15.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label15.Location = New System.Drawing.Point(173, 19)
        Me.Label15.Name = "Label15"
        Me.Label15.Size = New System.Drawing.Size(53, 12)
        Me.Label15.TabIndex = 45
        Me.Label15.Text = "저울종류"
        '
        'Label13
        '
        Me.Label13.AutoSize = True
        Me.Label13.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label13.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label13.Location = New System.Drawing.Point(172, 61)
        Me.Label13.Name = "Label13"
        Me.Label13.Size = New System.Drawing.Size(101, 12)
        Me.Label13.TabIndex = 44
        Me.Label13.Text = "안착 영점범위(%)"
        '
        'Label11
        '
        Me.Label11.AutoSize = True
        Me.Label11.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label11.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label11.Location = New System.Drawing.Point(6, 20)
        Me.Label11.Name = "Label11"
        Me.Label11.Size = New System.Drawing.Size(88, 12)
        Me.Label11.TabIndex = 43
        Me.Label11.Text = "최대중량값(kg)"
        '
        'Label10
        '
        Me.Label10.AutoSize = True
        Me.Label10.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label10.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label10.Location = New System.Drawing.Point(6, 40)
        Me.Label10.Name = "Label10"
        Me.Label10.Size = New System.Drawing.Size(41, 12)
        Me.Label10.TabIndex = 41
        Me.Label10.Text = "분해도"
        '
        'Label8
        '
        Me.Label8.AutoSize = True
        Me.Label8.Font = New System.Drawing.Font("굴림", 9.0!)
        Me.Label8.ForeColor = System.Drawing.SystemColors.Highlight
        Me.Label8.Location = New System.Drawing.Point(6, 61)
        Me.Label8.Name = "Label8"
        Me.Label8.Size = New System.Drawing.Size(73, 12)
        Me.Label8.TabIndex = 33
        Me.Label8.Text = "영점범위(%)"
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.ForeColor = System.Drawing.SystemColors.InfoText
        Me.Label2.Location = New System.Drawing.Point(129, 108)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(37, 27)
        Me.Label2.TabIndex = 31
        Me.Label2.Text = "gr"
        '
        'TextBox_weight
        '
        Me.TextBox_weight.Font = New System.Drawing.Font("굴림", 30.0!)
        Me.TextBox_weight.ForeColor = System.Drawing.SystemColors.MenuHighlight
        Me.TextBox_weight.Location = New System.Drawing.Point(16, 84)
        Me.TextBox_weight.Name = "TextBox_weight"
        Me.TextBox_weight.Size = New System.Drawing.Size(111, 53)
        Me.TextBox_weight.TabIndex = 30
        '
        'ComboBox_adr
        '
        Me.ComboBox_adr.FormattingEnabled = True
        Me.ComboBox_adr.Location = New System.Drawing.Point(10, 38)
        Me.ComboBox_adr.Name = "ComboBox_adr"
        Me.ComboBox_adr.Size = New System.Drawing.Size(38, 35)
        Me.ComboBox_adr.TabIndex = 29
        '
        'LC1Button_adr_ch
        '
        Me.LC1Button_adr_ch.Font = New System.Drawing.Font("굴림", 11.0!)
        Me.LC1Button_adr_ch.ForeColor = System.Drawing.SystemColors.InfoText
        Me.LC1Button_adr_ch.Location = New System.Drawing.Point(55, 38)
        Me.LC1Button_adr_ch.Name = "LC1Button_adr_ch"
        Me.LC1Button_adr_ch.Size = New System.Drawing.Size(84, 35)
        Me.LC1Button_adr_ch.TabIndex = 28
        Me.LC1Button_adr_ch.Text = "주소변경"
        Me.LC1Button_adr_ch.UseVisualStyleBackColor = True
        '
        'Button_read_id
        '
        Me.Button_read_id.Location = New System.Drawing.Point(3, 114)
        Me.Button_read_id.Name = "Button_read_id"
        Me.Button_read_id.Size = New System.Drawing.Size(83, 42)
        Me.Button_read_id.TabIndex = 24
        Me.Button_read_id.Text = "id읽기"
        Me.Button_read_id.UseVisualStyleBackColor = True
        '
        'Button_zero
        '
        Me.Button_zero.Location = New System.Drawing.Point(3, 207)
        Me.Button_zero.Name = "Button_zero"
        Me.Button_zero.Size = New System.Drawing.Size(83, 42)
        Me.Button_zero.TabIndex = 25
        Me.Button_zero.Text = "영점조정"
        Me.Button_zero.UseVisualStyleBackColor = True
        '
        'Button_weight
        '
        Me.Button_weight.Location = New System.Drawing.Point(3, 257)
        Me.Button_weight.Name = "Button_weight"
        Me.Button_weight.Size = New System.Drawing.Size(83, 42)
        Me.Button_weight.TabIndex = 26
        Me.Button_weight.Text = "중량읽기"
        Me.Button_weight.UseVisualStyleBackColor = True
        '
        'Button_read_param
        '
        Me.Button_read_param.Location = New System.Drawing.Point(3, 162)
        Me.Button_read_param.Name = "Button_read_param"
        Me.Button_read_param.Size = New System.Drawing.Size(83, 42)
        Me.Button_read_param.TabIndex = 27
        Me.Button_read_param.Text = "param읽기"
        Me.Button_read_param.UseVisualStyleBackColor = True
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(7.0!, 12.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(800, 450)
        Me.Controls.Add(Me.Button_read_param)
        Me.Controls.Add(Me.Button_weight)
        Me.Controls.Add(Me.Button_zero)
        Me.Controls.Add(Me.Button_read_id)
        Me.Controls.Add(Me.GroupBox2)
        Me.Controls.Add(Me.Rtb_tx_data)
        Me.Controls.Add(Me.Label20)
        Me.Controls.Add(Me.Label19)
        Me.Controls.Add(Me.Rtb_rx_data)
        Me.Controls.Add(Me.GroupBox1)
        Me.Name = "Form1"
        Me.Text = "Form1"
        Me.GroupBox1.ResumeLayout(False)
        Me.GroupBox1.PerformLayout()
        Me.GroupBox2.ResumeLayout(False)
        Me.GroupBox2.PerformLayout()
        Me.GroupBox7.ResumeLayout(False)
        Me.GroupBox7.PerformLayout()
        Me.GroupBox6.ResumeLayout(False)
        Me.GroupBox6.PerformLayout()
        Me.GroupBox5.ResumeLayout(False)
        Me.GroupBox5.PerformLayout()
        Me.GroupBox4.ResumeLayout(False)
        Me.GroupBox4.PerformLayout()
        Me.GroupBox3.ResumeLayout(False)
        Me.GroupBox3.PerformLayout()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents CbBox_com_port As ComboBox
    Friend WithEvents Label1 As Label
    Friend WithEvents Btn_comm_set As Button
    Friend WithEvents SerialPort1 As IO.Ports.SerialPort
    Friend WithEvents GroupBox1 As GroupBox
    Friend WithEvents Btn_comm_stop As Button
    Friend WithEvents Rtb_rx_data As RichTextBox
    Friend WithEvents Label19 As Label
    Friend WithEvents Timer1 As Timer
    Friend WithEvents Label20 As Label
    Friend WithEvents Rtb_tx_data As RichTextBox
    Friend WithEvents GroupBox2 As GroupBox
    Friend WithEvents LC1Button_adr_ch As Button
    Friend WithEvents Button_read_id As Button
    Friend WithEvents ComboBox_adr As ComboBox
    Friend WithEvents Button_zero As Button
    Friend WithEvents Button_weight As Button
    Friend WithEvents Label8 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents TextBox_weight As TextBox
    Friend WithEvents RButton_err_zero As RadioButton
    Friend WithEvents RButton_overload As RadioButton
    Friend WithEvents RButton_error As RadioButton
    Friend WithEvents RButton_ok As RadioButton
    Friend WithEvents RButton_cal As RadioButton
    Friend WithEvents Label11 As Label
    Friend WithEvents GroupBox3 As GroupBox
    Friend WithEvents Label10 As Label
    Friend WithEvents Label_down_zero As Label
    Friend WithEvents Label_kind As Label
    Friend WithEvents Label_range_zero As Label
    Friend WithEvents Label_division As Label
    Friend WithEvents Label_max_weight As Label
    Friend WithEvents Label15 As Label
    Friend WithEvents Label13 As Label
    Friend WithEvents GroupBox7 As GroupBox
    Friend WithEvents ComboBox_kind As ComboBox
    Friend WithEvents ComboBox_down_range As ComboBox
    Friend WithEvents ComboBox_zero_range As ComboBox
    Friend WithEvents ComboBox_division As ComboBox
    Friend WithEvents ComboBox_max_weight As ComboBox
    Friend WithEvents Button_param As Button
    Friend WithEvents Label7 As Label
    Friend WithEvents Label6 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents GroupBox6 As GroupBox
    Friend WithEvents GroupBox5 As GroupBox
    Friend WithEvents Label_adr As Label
    Friend WithEvents Label29 As Label
    Friend WithEvents GroupBox4 As GroupBox
    Friend WithEvents Label_id3 As Label
    Friend WithEvents Label_id2 As Label
    Friend WithEvents Label_id1 As Label
    Friend WithEvents Label_id0 As Label
    Friend WithEvents Label21 As Label
    Friend WithEvents Label18 As Label
    Friend WithEvents Label17 As Label
    Friend WithEvents Label14 As Label
    Friend WithEvents Label16 As Label
    Friend WithEvents Labe_ad_value As Label
    Friend WithEvents Label12 As Label
    Friend WithEvents Button_read_param As Button
End Class
