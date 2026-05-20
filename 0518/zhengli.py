import re
from datetime import datetime
import sys


def parse_log_entry(log_entry):
    """
    解析单个日志条目，提取关键信息
    """
    result =''
    # 提取时间戳
    time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', log_entry)
    if time_match:
        result['timestamp'] = time_match.group(1)

    # 提取服务单元和名称
    unit_match = re.search(r'<Unit>([^<]+)</Unit>', log_entry)
    name_match = re.search(r'<Name>([^<]+)</Name>', log_entry)
    type_match = re.search(r'<Type>([^<]+)</Type>', log_entry)

    if unit_match:
        result['unit'] = unit_match.group(1)
    if name_match:
        result['name'] = name_match.group(1)
    if type_match:
        result['type'] = type_match.group(1)

    # 根据不同的通知类型提取Body内容
    if 'MesCMSalarmRep' in log_entry:
        # 报警报告类型
        module_match = re.search(r'<Module>([^<]+)</Module>', log_entry)
        stat_match = re.search(r'<STAT>([^<]+)</STAT>', log_entry)
        error_type_match = re.search(r'<ErrorType>([^<]+)</ErrorType>', log_entry)
        stop_bit_match = re.search(r'<StopBit>([^<]+)</StopBit>', log_entry)
        error_id_match = re.search(r'<Errorid>([^<]+)</Errorid>', log_entry)
        error_msg_match = re.search(r'<ErrorMessage>([^<]+)</ErrorMessage>', log_entry)
        error_code_match = re.search(r'<ErrorCode>([^<]+)</ErrorCode>', log_entry)
        glass_ser_match = re.search(r'<GlassSer>([^<]+)</GlassSer>', log_entry)

        if module_match:
            result['module'] = module_match.group(1)
        if stat_match:
            result['status'] = stat_match.group(1)
        if error_type_match:
            result['error_type'] = error_type_match.group(1)
        if stop_bit_match:
            result['stop_bit'] = stop_bit_match.group(1)
        if error_id_match:
            result['error_id'] = error_id_match.group(1)
        if error_msg_match:
            result['error_message'] = error_msg_match.group(1)
        if error_code_match:
            result['error_code'] = error_code_match.group(1)
        if glass_ser_match:
            result['glass_serial'] = glass_ser_match.group(1)

    elif 'MesCMSnotifyJob' in log_entry:
        # 作业通知类型
        status_match = re.search(r'<Status>([^<]+)</Status>', log_entry)
        job_id_match = re.search(r'<JobID>([^<]+)</JobID>', log_entry)

        if status_match:
            result['job_status'] = status_match.group(1)
        if job_id_match:
            result['job_id'] = job_id_match.group(1)

        # 提取Info部分
        info_section = re.search(r'<Info>(.*?)</Info>', log_entry, re.DOTALL)
        if info_section:
            info_text = info_section.group(1)
            glass_ser_match = re.search(r'<GlassSer>([^<]+)</GlassSer>', info_text)
            ppid1_match = re.search(r'<PPID1>([^<]+)</PPID1>', info_text)
            port_match = re.search(r'<PORT>([^<]+)</PORT>', info_text)
            lotid_match = re.search(r'<LOTID>([^<]+)</LOTID>', info_text)
            slot_match = re.search(r'<SLOT>([^<]+)</SLOT>', info_text)
            glsid_match = re.search(r'<GLSID>([^<]+)</GLSID>', info_text)

            if glass_ser_match:
                result['glass_serial'] = glass_ser_match.group(1)
            if ppid1_match:
                result['ppid1'] = ppid1_match.group(1)
            if port_match:
                result['port'] = port_match.group(1)
            if lotid_match:
                result['lot_id'] = lotid_match.group(1)
            if slot_match:
                result['slot'] = slot_match.group(1)
            if glsid_match:
                result['glass_id'] = glsid_match.group(1)

    return result


def format_log_entry(entry_data):
    """
    格式化单个日志条目为易读的文本
    """
    output = []

    # 时间戳和基本信息
    output.append(f"【时间戳】 {entry_data.get('timestamp', 'N/A')}")
    output.append(f"【服务单元】 {entry_data.get('unit', 'N/A')}")
    output.append(f"【通知类型】 {entry_data.get('name', 'N/A')} ({entry_data.get('type', 'N/A')})")

    # 根据不同类型格式化内容
    if entry_data.get('name') == 'MesCMSalarmRep':
        output.append(f"【模块】 {entry_data.get('module', 'N/A')}")
        output.append(f"【MES状态】 {entry_data.get('status', 'N/A')}")
        output.append(f"【错误类型】 {entry_data.get('error_type', 'N/A')}")
        output.append(f"【停止位】 {entry_data.get('stop_bit', 'N/A')}")
        output.append(f"【错误ID】 {entry_data.get('error_id', 'N/A')}")
        output.append(f"【错误代码】 {entry_data.get('error_code', 'N/A')}")
        output.append(f"【玻璃序列号】 {entry_data.get('glass_serial', 'N/A')}")

        # 错误消息重点显示
        error_msg = entry_data.get('error_message', '')
        if error_msg:
            output.append(f"【错误信息】 ⚠️ {error_msg}")

    elif entry_data.get('name') == 'MesCMSnotifyJob':
        output.append(f"【作业状态】 {entry_data.get('job_status', 'N/A')}")
        output.append(f"【作业ID】 {entry_data.get('job_id', 'N/A')}")

        # 作业详细信息
        output.append("【作业详情】")
        if 'glass_serial' in entry_data:
            output.append(f"  * 玻璃序列号: {entry_data['glass_serial']}")
        if 'ppid1' in entry_data:
            output.append(f"  * PPID1: {entry_data['ppid1']}")
        if 'port' in entry_data:
            output.append(f"  * 端口: {entry_data['port']}")
        if 'lot_id' in entry_data:
            output.append(f"  * LOT ID: {entry_data['lot_id']}")
        if 'slot' in entry_data:
            output.append(f"  * 槽位: {entry_data['slot']}")
        if 'glass_id' in entry_data:
            output.append(f"  * 玻璃ID: {entry_data['glass_id']}")

    return "\n".join(output)


def parse_and_format_logs(log_text):
    """
    主函数：解析并格式化整个日志文本
    """
    # 分割日志条目（假设每个条目以时间戳开始）
    entries = []
    current_entry = ''
    lines = log_text.strip().split('\n')
    for line in lines:
        # 检查是否是新条目的开始（包含时间戳模式）
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [A-Z]:', line):
            if current_entry:
                entries.append(current_entry)
            current_entry = line
        else:
            current_entry += "\n" + line

    # 添加最后一个条目
    if current_entry:
        entries.append(current_entry)

    # 解析和格式化每个条目
    formatted_output = []
    for i, entry in enumerate(entries, 1):
        entry_data = parse_log_entry(entry)
        formatted_entry = format_log_entry(entry_data)

        formatted_output.append(f"\n{'=' * 60}")
        formatted_output.append(f"日志条目 #{i}")
        formatted_output.append(f"{'=' * 60}")
        formatted_output.append(formatted_entry)

    return "\n".join(formatted_output)


def main():
    """
    主执行函数
    """
    # 如果提供了命令行参数，则从文件读取
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                log_text = f.read()
        except FileNotFoundError:
            print(f"错误：文件 '{sys.argv[1]}' 未找到")
            return
        except Exception as e:
            print(f"读取文件时出错：{e}")
            return
    else:
        # 使用提供的示例日志
        log_text = """<Body>
2026-05-18 13:27:05.857 D: <FPDService><Unit>CIM</Unit><Name>MesCMSalarmRep</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
<Module>CIUAOI</Module>
<STAT>MesOn</STAT>
<ErrorType>Light</ErrorType>
<StopBit>NO</StopBit>
<Errorid>1</Errorid>
<ErrorMessage>DFS response fail(getFixedGrab:NotConnect)</ErrorMessage>
<ErrorCode>32050</ErrorCode>
<GlassSer>48291</GlassSer>
</Body>
2026-05-18 13:27:05.857 D: <FPDService><Unit>CIM</Unit><Name>MesCMSalarmRep</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
<Module>CIUAOI</Module>
<STAT>MesOn</STAT>
<ErrorType>Light</ErrorType>
<StopBit>NO</StopBit>
<Errorid>1</Errorid>
<ErrorMessage>reference file creation failed(X:\judge_dbase\AMPI04\PVX\75BM\9AB1651031\9AB1651031A1.asc.defect)</ErrorMessage>
<ErrorCode>32024</ErrorCode>
<GlassSer>48291</GlassSer>
</Body>
2026-05-18 13:27:05.906 D: <FPDService><Unit>CIM</Unit><Name>MesCMSalarmRep</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
<Module>CIUAOI</Module>
<STAT>MesOn</STAT>
<ErrorType>Light</ErrorType>
<StopBit>NO</StopBit>
<Errorid>1</Errorid>
<ErrorMessage>DFS response fail(getInspInfo:NotConnect)</ErrorMessage>
<ErrorCode>32010</ErrorCode>
<GlassSer>48291</GlassSer>
</Body>
2026-05-18 13:27:05.906 D: <FPDService><Unit>CIM</Unit><Name>MesCMSnotifyJob</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
	<Status>ABORT</Status>
	<JobID>18</JobID>
	<Info>
		<GlassSer>48291</GlassSer>
		<PPID1>75BM_PVX_TF</PPID1>
		<PPID2></PPID2>
		<PPID3></PPID3>
		<PORT>1</PORT>
		<LOTID>9AB1651031</LOTID>
		<SLOT>1</SLOT>
		<GLSID>9AB1651031A1</GLSID>
	</Info>
	<FABINFO/>

</Body>
2026-05-18 13:27:06.106 D: <FPDService><Unit>CIM</Unit><Name>MesCMSalarmRep</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
<Module>LOADER</Module>
<STAT>MesOff</STAT>
<ErrorType>Light</ErrorType>
<StopBit>NO</StopBit>
<Errorid>1</Errorid>
<ErrorMessage>DataCnv.exe is disconnected</ErrorMessage>
<ErrorCode>2101</ErrorCode>
<GlassSer>47455</GlassSer>
</Body>
2026-05-18 13:27:12.208 D: <FPDService><Unit>CIM</Unit><Name>MesCMSalarmRep</Name><Type>Notify</Type><Version>1.00</Version></FPDService><Body>
<Module>LOADER</Module>
<STAT>MesOn</STAT>
<ErrorType>Light</ErrorType>
<StopBit>NO</StopBit>
<Errorid>1</Errorid>
<ErrorMessage>DataCnv.exe is disconnected</ErrorMessage>
<ErrorCode>2101</ErrorCode>
<GlassSer>48291</GlassSer>
</Body>"""

    # 解析并格式化日志
    formatted_logs = parse_and_format_logs(log_text)

    # 输出结果
    print("=" * 60)
    print("格式化后的日志内容")
    print("=" * 60)
    print(formatted_logs)

    # 可选：保存到文件
    save_to_file = input("\n是否保存到文件？(y/n): ").lower()
    if save_to_file == 'y':
        filename = input("请输入文件名（默认为 formatted_log.txt）: ").strip()
        if not filename:
            filename = "formatted_log.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_logs)
            print(f"日志已保存到 {filename}")
        except Exception as e:
            print(f"保存文件时出错：{e}")


if __name__ == "__main__":
    main()