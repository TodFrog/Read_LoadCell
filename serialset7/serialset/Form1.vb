Imports System
Imports System.ComponentModel
Imports System.Threading
Imports System.IO.Ports

Public Class Form1
    Dim myPort As Array  '시스템의 검색된 통신포트가 여기에 저장된다
    Dim rx_data(500) As Byte
    Dim adr_buff(500) As Byte
    Dim rx_count As Integer
    Dim t_interval_rx As Integer
    Dim Loadcell_id(8) As Byte
    Dim temp_adr As Byte
    Dim status_LC1 As Byte
    Dim division_LC1 As Byte
    Dim weight_read_LC1 As ULong
    Dim weight_result As Short
    Dim resolution As UShort
    Dim division_array() As Integer =
        {1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000}

    Dim max_weight_table() As Byte =
        {5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
       55, 60, 65, 70, 75, 80, 85, 90, 95, 100}

    Dim resolution_table() As UShort =
        {0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50,
      100, 200, 500, 1000, 2000, 5000}
    '   {0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05,
    '  0.1, 0.2, 0.5, 1.0, 2.0, 5.0}
    Dim scaler_kind() As String =
        {"쾌속측정", "보통측정", "crane 측정", "대형 crane 측정"}
    Delegate Sub Label_max_weight_changeCallback(ByVal [text] As String)
    Delegate Sub division_changeCallback(ByVal [text] As String)
    Delegate Sub read_data_information_changeCallback(ByVal [text] As String)
    Delegate Sub weight_information_changeCallback(ByVal [text] As String)
    Delegate Sub resol_information_changeCallback(ByVal [text] As String)
    Delegate Sub id0_information_changeCallback(ByVal [text] As String)
    Delegate Sub id1_information_changeCallback(ByVal [text] As String)
    Delegate Sub id2_information_changeCallback(ByVal [text] As String)
    Delegate Sub id3_information_changeCallback(ByVal [text] As String)
    Delegate Sub adr_information_changeCallback(ByVal [text] As String)
    Delegate Sub Label_range_zero_info_changeCallback(ByVal [text] As String)
    Delegate Sub Label_down_zero_info_changeCallback(ByVal [text] As String)
    Delegate Sub Label_kind_info_changeCallback(ByVal [text] As String)

    Delegate Sub ReceivedTextCallback(ByVal [text] As String) '데이터 수신중 쓰레드(thread) 에러 방지용으로 추가함

    Private Sub frmForm1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        '폼 로딩시, 시리얼 포트가 자동 검색되고 cmbPort 콤보박스에 표시된다.
        Dim i As Byte

        myPort = IO.Ports.SerialPort.GetPortNames() 'Get all com ports available
        ComboBox_adr.Items.Add(1)
        ComboBox_adr.Items.Add(2)
        ComboBox_adr.Items.Add(3)
        ComboBox_adr.Items.Add(4)
        ComboBox_adr.Items.Add(5)
        ComboBox_adr.Items.Add(6)
        ComboBox_adr.Items.Add(7)
        ComboBox_adr.Items.Add(8)
        ComboBox_adr.Items.Add(9)
        ComboBox_adr.Items.Add(10)


        ComboBox_division.Items.Add("0(0.0001)")
        ComboBox_division.Items.Add("1(0.0002)")
        ComboBox_division.Items.Add("2(0.0005)")
        ComboBox_division.Items.Add("3(0.001)")
        ComboBox_division.Items.Add("4(0.002)")
        ComboBox_division.Items.Add("5(0.005)")
        ComboBox_division.Items.Add("6(0.01)")
        ComboBox_division.Items.Add("7(0.02)")
        ComboBox_division.Items.Add("8(0.05)")
        ComboBox_division.Items.Add("9(0.1)")
        ComboBox_division.Items.Add("A(0.2)")
        ComboBox_division.Items.Add("B(0.5)")
        ComboBox_division.Items.Add("C(1.0)")
        ComboBox_division.Items.Add("D(2.0)")
        ComboBox_division.Items.Add("E(5.0)")
        For i = 0 To 14
            ComboBox_max_weight.Items.Add(max_weight_table(i))
        Next
        For i = 0 To 9
            ComboBox_zero_range.Items.Add(i)
        Next
        For i = 1 To 10
            ComboBox_down_range.Items.Add(i)
        Next
        ComboBox_kind.Items.Add("쾌속측정")
        ComboBox_kind.Items.Add("보통측정")
        ComboBox_kind.Items.Add("crane 측정")
        ComboBox_kind.Items.Add("대형 crane 측정")

        For i = 0 To UBound(myPort)
            CbBox_com_port.Items.Add(myPort(i))
        Next

        CbBox_com_port.Text = CbBox_com_port.Items.Item(0)    'Set cmbPort text to the first COM port detected
        Btn_comm_set.Enabled = True           'Initially Disconnect Button is Disabled

        Btn_comm_set.Enabled = True
        Btn_comm_stop.Enabled = False

        Timer1.Enabled = True
        Timer1.Interval = 500

        t_interval_rx = 0
        rx_count = 0



    End Sub

    Private Sub Btn_comm_set_Click(sender As Object, e As EventArgs) Handles Btn_comm_set.Click

        SerialPort1.PortName = CbBox_com_port.Text         'Set SerialPort1 to the selected COM port at startup
        SerialPort1.BaudRate = 115200         'Set Baud rate to the selected value on
        'Other Serial Port Property
        SerialPort1.Parity = IO.Ports.Parity.None
        SerialPort1.StopBits = IO.Ports.StopBits.One
        SerialPort1.DataBits = 8            'Open our serial port

        SerialPort1.Open()
        Btn_comm_set.Enabled = False
        Btn_comm_stop.Enabled = True

    End Sub
    Private Sub check_box_clear()

    End Sub
    Public Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)

    'Private Sub Btn_tx_Click(sender As Object, e As EventArgs) Handles Btn_tx.Click
    Function Tx_command_every_sec(ByVal rps As Byte)
        Dim tx_data(20) As Byte
        Dim buf_tx_data(20) As UShort
        Dim max_tx_bytes As Byte

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()


        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H5   'function code  " read "
        tx_data(2) = &H5   'id read
        tx_data(3) = &H5   '고정값
        tx_data(4) = tx_data(0) + tx_data(1) + tx_data(2) + tx_data(3)
        max_tx_bytes = 5
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)


        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next

        check_box_clear()



        'End Sub
    End Function


    Private Sub Btn_comm_stop_Click(sender As Object, e As EventArgs) Handles Btn_comm_stop.Click
        SerialPort1.Close()
        Btn_comm_set.Enabled = True
        Btn_comm_stop.Enabled = False

    End Sub


    Private Sub ReceivedText(ByVal [text] As String)
        'compares the ID of the creating Thread to the ID of the calling Thread
        Dim i As Byte
        If Me.Rtb_rx_data.InvokeRequired Then
            Dim x As New ReceivedTextCallback(AddressOf ReceivedText)

            Me.Invoke(x, New Object() {Hex((text))})
            Me.Invoke(x, New Object() {"-"})

        Else
            Me.Rtb_rx_data.Text &= [text]


        End If

    End Sub
    Private Sub Label_max_weight_change(ByVal [text] As String)
        If Me.Label_max_weight.InvokeRequired Then
            Dim x As New id0_information_changeCallback(AddressOf Label_max_weight_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_max_weight.Text &= [text]
        End If
    End Sub
    Private Sub id0_information_change(ByVal [text] As String)
        If Me.Label_id0.InvokeRequired Then
            Dim x As New id0_information_changeCallback(AddressOf id0_information_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_id0.Text &= [text]
        End If
    End Sub
    Private Sub id1_information_change(ByVal [text] As String)
        If Me.Label_id1.InvokeRequired Then
            Dim x As New id1_information_changeCallback(AddressOf id1_information_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_id1.Text &= [text]
        End If
    End Sub
    Private Sub id2_information_change(ByVal [text] As String)
        If Me.Label_id2.InvokeRequired Then
            Dim x As New id2_information_changeCallback(AddressOf id2_information_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_id2.Text &= [text]
        End If
    End Sub
    Private Sub id3_information_change(ByVal [text] As String)
        If Me.Label_id3.InvokeRequired Then
            Dim x As New id3_information_changeCallback(AddressOf id3_information_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_id3.Text &= [text]
        End If
    End Sub
    Private Sub adr_information_change(ByVal [text] As String)
        If Me.Label_adr.InvokeRequired Then
            Dim x As New adr_information_changeCallback(AddressOf adr_information_change)

            Me.Invoke(x, New Object() {Hex((text))})
        Else
            Me.Label_adr.Text &= [text]
        End If
    End Sub

    Private Sub weight_information_change(ByVal [text] As String)
        If Me.TextBox_weight.InvokeRequired Then
            Dim x As New weight_information_changeCallback(AddressOf weight_information_change)

            Me.Invoke(x, New Object() {((text))})
        Else
            Me.TextBox_weight.Text &= [text]
        End If
    End Sub
    Private Sub resol_information_change(ByVal [text] As String)
        If Me.Label_division.InvokeRequired Then
            Dim x As New resol_information_changeCallback(AddressOf resol_information_change)

            Me.Invoke(x, New Object() {(Hex(text))})
        Else
            Me.Label_division.Text &= [text]
        End If
    End Sub
    Private Sub read_data_information_change(ByVal [text] As String)
        If Me.Labe_ad_value.InvokeRequired Then
            Dim x As New read_data_information_changeCallback(AddressOf read_data_information_change)

            Me.Invoke(x, New Object() {(Hex(text))})

        Else
            Me.Labe_ad_value.Text &= [text]
        End If
    End Sub
    Private Sub division_change(ByVal [text] As String)
        If Me.ComboBox_division.InvokeRequired Then
            Dim x As New division_changeCallback(AddressOf division_change)

            Me.Invoke(x, New Object() {((text))})
        Else
            Me.ComboBox_division.Text &= [text]
        End If
    End Sub
    Sub Label_range_zero_info_change(ByVal [text] As String)
        If Me.Label_range_zero.InvokeRequired Then
            Dim x As New division_changeCallback(AddressOf Label_range_zero_info_change)

            Me.Invoke(x, New Object() {((text))})
        Else
            Me.Label_range_zero.Text &= [text]
        End If
    End Sub
    Sub Label_down_zero_info_change(ByVal [text] As String)
        If Me.Label_down_zero.InvokeRequired Then
            Dim x As New division_changeCallback(AddressOf Label_down_zero_info_change)

            Me.Invoke(x, New Object() {((text))})
        Else
            Me.Label_down_zero.Text &= [text]
        End If
    End Sub
    Sub Label_kind_info_change(ByVal [text] As String)
        If Me.Label_kind.InvokeRequired Then
            Dim x As New division_changeCallback(AddressOf Label_kind_info_change)

            Me.Invoke(x, New Object() {((text))})
        Else
            Me.Label_kind.Text &= [text]
        End If
    End Sub

    Public Function Char_to_Hex(ByVal char_data) As Byte
        Return Hex((((char_data / 16) * &H10) + (char_data Mod 16)))
    End Function


    Private Sub SerialPort1_DataReceived(ByVal sender As Object, ByVal e As System.IO.Ports.SerialDataReceivedEventArgs)
        Handles SerialPort1.DataReceived



        Dim buffer(50) As Byte
        Dim n As Integer
        Dim return_value As Integer
        Dim i As Byte



        n = SerialPort1.BytesToRead
        If n > 0 Then
            For i = 0 To n - 1
                rx_data(rx_count) = SerialPort1.ReadByte
                rx_count += 1
            Next
            For i = 0 To rx_count - 1
                ReceivedText(rx_data(i))
            Next

        End If

        If rx_data(2) = &H5 Then 'id read
            If (Loadcell_id(0) = rx_data(7)) Then

            Else
                Loadcell_id(0) = rx_data(7)
                id0_information_change(Loadcell_id(0))
            End If
            If (Loadcell_id(1) = rx_data(8)) Then

            Else
                Loadcell_id(1) = rx_data(8)
                id1_information_change(Loadcell_id(1))
            End If
            If (Loadcell_id(2) = rx_data(9)) Then
            Else
                Loadcell_id(2) = rx_data(9)
                id2_information_change(Loadcell_id(2))
            End If
            If (Loadcell_id(3) = rx_data(10)) Then

            Else
                Loadcell_id(3) = rx_data(10)
                id3_information_change(Loadcell_id(3))
            End If
            If (Loadcell_id(4) = rx_data(0)) Then

            Else
                Loadcell_id(4) = rx_data(0) ' loadcell address
                adr_information_change(Loadcell_id(4))
            End If

        ElseIf rx_data(2) = &H2 Then ' weight read
            status_LC1 = rx_data(3)
            division_LC1 = rx_data(4) And &HF
            weight_read_LC1 = (rx_data(5) * &H100) + (rx_data(6) * &H10) + (rx_data(7) * &H1)
            resolution = resolution_table(division_LC1)


            ' If (rx_data(4) And &H80) = 0 Then
            weight_result = (resolution * weight_read_LC1)
            ' Else
            ' weight_result = -(resolution * weight_read_LC1)
            'End If
            weight_information_change(weight_result)
                resol_information_change(division_LC1)
                read_data_information_change(weight_read_LC1)
                ' division_change(resolution_table(division_LC1))
            ElseIf rx_data(2) = &H23 Then ' parameter read
                resol_information_change(resolution_table((rx_data(3) And &HF0) >> 4))
            Label_range_zero_info_change((rx_data(4) And &HF0) >> 4)
            Label_down_zero_info_change(rx_data(4) And &HF)
            Label_kind_info_change(scaler_kind(rx_data(3) And &HF))
            Label_max_weight_change(((rx_data(5) * &H10000) + (rx_data(6) * &H100) + rx_data(7)) * resolution_table((rx_data(3) And &HF0) >> 4))
        End If
    End Sub
    Function status_check(ByVal status As Byte)
        If (status And &H1) Then
            RButton_err_zero.Checked = True
        Else
            RButton_err_zero.Checked = False

        End If

    End Function

    Private Sub Timer1_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Tick
        Dim temp As Byte


        '        Timer1.Enabled = False
        '    Timer1.Interval = 2500

        t_interval_rx = t_interval_rx + 1

        status_check(status_LC1)


        '   If SerialPort1.IsOpen = True Then
        ' Tx_command_every_sec(7)
        ' End If

    End Sub

    Private Function Adr_change(ByVal Adr As Byte)
        Dim tx_data(20) As Byte
        Dim checksum As UInt16
        Dim i, j As Byte
        Dim max_tx_bytes As Byte

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        Label_adr.ResetText()


        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H63   'function code  " write "
        tx_data(2) = &H10   'address write 
        tx_data(3) = Adr 'ListBox_adr.Text
        tx_data(4) = tx_data(0) + tx_data(1) + tx_data(2) + tx_data(3)
        max_tx_bytes = 5
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)


        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next
    End Function
    Private Sub LC1Button_adr_ch_Click(sender As Object, e As EventArgs) Handles LC1Button_adr_ch.Click
        Adr_change(ComboBox_adr.Text)
    End Sub

    Private Sub Button_read_id_Click(sender As Object, e As EventArgs) Handles Button_read_id.Click
        Dim i As Byte

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        Label_adr.ResetText()
        Label_id0.ResetText()
        Label_id1.ResetText()
        Label_id2.ResetText()
        Label_id3.ResetText()

        For i = 0 To 7
            Loadcell_id(i) = 99
        Next

        adr_information_change(0)


        Tx_command_every_sec(7)
    End Sub

    Private Sub Button_zero_Click(sender As Object, e As EventArgs) Handles Button_zero.Click
        Dim tx_data(20) As Byte
        Dim i As Byte
        Dim max_tx_bytes As Byte

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H63   'function code  " write "
        tx_data(2) = &H6   'zero set register
        tx_data(3) = &H3  ' zeroset information
        tx_data(4) = tx_data(0) + tx_data(1) + tx_data(2) + tx_data(3)
        max_tx_bytes = 5
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)


        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next
    End Sub

    Private Sub Button_weight_Click(sender As Object, e As EventArgs) Handles Button_weight.Click
        Dim tx_data(20) As Byte
        Dim i As Byte
        Dim max_tx_bytes As Byte

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        TextBox_weight.Clear()
        Label_division.ResetText()
        Labe_ad_value.ResetText()


        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H5   'function code  " read "
        tx_data(2) = &H2   'weight read register
        tx_data(3) = &H5  ' const information
        tx_data(4) = tx_data(0) + tx_data(1) + tx_data(2) + tx_data(3)
        max_tx_bytes = 5
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)


        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next

    End Sub

    Private Sub Button_param_Click(sender As Object, e As EventArgs)
        Dim tx_data(20) As Byte
        Dim i As Byte
        Dim max_tx_bytes As Byte
        Dim temp As UInt32

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        TextBox_weight.Clear()
        Label_division.ResetText()
        ' 0.0001 : 00 63 23 01 09 01 86 a0 b7
        ' 0.0002 : 00 63 23 11 09 00 c3 50 b3
        ' 0.0005 : 00 63 23 21 09 00 4e 20 1e
        ' 0.001 : 00 63 23 31 09 00 27 10 f7
        ' 0.002 : 00 63 23 41 09 00 13 88 6b
        ' 0.005 : 00 63 23 51 09 00 07 d0 b7
        ' 0.01 : 00 63 23 61 09 00 03 e8 db
        ' 0.02 : 00 63 23 71 09 00 01 f4 f5
        ' 0.05 : 00 63 23 81 09 00 00 c8 d8
        ' 0.1 : 00 63 23 91 09 00 00 64 84
        ' 0.2 : 00 63 23 a1 09 00 00 32 62
        ' 0.5 : 00 63 23 b1 09 00 00 14 54
        ' 1.0 : 00 63 23 c1 09 00 00 0a 5a
        ' 2.0 : 00 63 23 d1 09 00 00 05 65
        ' 5.0 : 00 63 23 e1 09 00 00 02 72

        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H63   'function code  " write "
        tx_data(2) = &H23   'Digital load cell Parameters register
        tx_data(3) = &H1 + (ComboBox_division.SelectedIndex * &H10) ' division value
        tx_data(4) = &H9  ' 
        tx_data(5) = 0  ' 
        tx_data(6) = &H3  ' 
        tx_data(7) = &HE8  '
        temp = 0
        For i = 0 To 7
            temp = temp + tx_data(i)
        Next
        tx_data(8) = temp And &HFF

        max_tx_bytes = 9
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)

        resolution = resolution_table(ComboBox_division.SelectedIndex)
        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next

    End Sub

    Private Sub Button_read_param_Click(sender As Object, e As EventArgs) Handles Button_read_param.Click
        Dim tx_data(20) As Byte
        Dim i As Byte
        Dim max_tx_bytes As Byte
        Dim temp As UInt32

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()
        Label_division.ResetText()
        Label_max_weight.ResetText()
        Label_range_zero.ResetText()
        Label_down_zero.ResetText()
        Label_kind.ResetText()

        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H5   'function code  " read "
        tx_data(2) = &H23   'Digital load cell Parameters register
        tx_data(3) = &H5   '고정값
        tx_data(4) = tx_data(0) + tx_data(1) + tx_data(2) + tx_data(3)
        max_tx_bytes = 5
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)

        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next

    End Sub

    Private Sub Button_param_Click_1(sender As Object, e As EventArgs) Handles Button_param.Click
        Dim tx_data(20) As Byte
        Dim i As Byte
        Dim max_tx_bytes As Byte
        Dim temp As UInt32

        Rtb_tx_data.Clear()
        Rtb_rx_data.Clear()


        Label_division.ResetText()
        Label_max_weight.ResetText()
        Label_range_zero.ResetText()
        Label_down_zero.ResetText()
        Label_kind.ResetText()

        tx_data(0) = &H0    'broadcasting command
        tx_data(1) = &H63   'function code  " write "
        tx_data(2) = &H23   'Digital load cell Parameters register
        tx_data(3) = ComboBox_max_weight.SelectedIndex
        tx_data(4) = ComboBox_division.SelectedIndex
        tx_data(5) = ComboBox_zero_range.SelectedIndex
        tx_data(6) = ComboBox_down_range.SelectedIndex
        tx_data(7) = ComboBox_kind.SelectedIndex


        ' tx_data(3) = ((ComboBox_division.SelectedIndex << 4) And &HF0) + (ComboBox_kind.SelectedIndex)  '상위ibble : division, 하위 nibble : 중량계종류 
        'tx_data(4) = ((ComboBox_zero_range.SelectedIndex << 4) And &HF0) + (ComboBox_down_range.SelectedIndex)  '상위ibble : division, 하위 nibble : 중량계종류 
        'temp = (max_weight_table(ComboBox_max_weight.SelectedIndex) * 1000) / resolution_table(ComboBox_division.SelectedIndex) '상위ibble : division, 하위 nibble : 중량계종류 
        'tx_data(5) = (temp And &HFF0000) >> 16
        'tx_data(6) = (temp And &HFF00) >> 8
        'tx_data(7) = (temp And &HFF)
        temp = 0
        For i = 0 To 7
            temp = temp + tx_data(i)
        Next
        tx_data(8) = temp And &HFF
        max_tx_bytes = 9
        rx_count = 0
        SerialPort1.Write(tx_data, 0, max_tx_bytes)

        For i = 0 To 17
            rx_data(i) = 0
            i = i + 1
        Next

        For i = 0 To max_tx_bytes - 1

            Rtb_tx_data.AppendText(Hex(tx_data(i)))
            Rtb_tx_data.AppendText(" ")
        Next


    End Sub
End Class
