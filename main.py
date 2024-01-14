from modules import scan as scc
from modules import tabel_to_file as ttf
import threading
import time
from datetime import datetime
import dearpygui.dearpygui as dpg
import re

dpg.create_context()
dpg.create_viewport(title='Net Scanner', width=600, height=400)
test = []
stop_event = threading.Event()


def save():
    global test
    current = datetime.now()
    timeformat = current.strftime('%D %H:%M:%S')
    res_name = re.sub(r"[/:]", '.', timeformat)
    ttf.TabelWriter(f'scan from {res_name}', test)


def count():
    if not stop_event.is_set():
        for c in range(0, 254):
            dpg.set_value(sc, f"scanned: {c}")
            dpg.set_viewport_resize_callback(lambda: dpg.set_item_pos(botLabs, (10, dpg.get_viewport_height() - 60)))
            time.sleep(0.11)


def scan():
    global test
    global stop_event
    if not stop_event.is_set():
        test.clear()
        scan_item = scc.Scanner()
        scan_item.clear_hosts()
        scan_item.scan_net()
        for host_info in scan_item.get_hosts():
            test.append(host_info)


def clear_table(table_tag):
    children = dpg.get_item_children(table_tag, 1)
    for item in children:
        dpg.delete_item(item=item)


def clear_from_button():
    global stop_event
    stop_event.set()
    clear_table('tag')
    dpg.set_value(sc, "scanned: 0")
    dpg.set_value(stat, "Status:NoScan")


def fill_table():
    for i in range(0, len(test)):
        thing = test[i]
        with dpg.table_row(parent='tag'):
            for j in thing:
                dpg.add_text(j)


def change_flag():
    global stop_event
    stop_event.set()
    dpg.set_value(stat, f"scan status: Finishing")


def scanner():
    global stop_event
    global test
    while not stop_event.is_set():
        ThrCounter = threading.Thread(target=count)
        ThrScan = threading.Thread(target=scan)

        ThrScan.start()
        ThrCounter.start()

        ThrCounter.join()
        ThrScan.join()

        del ThrScan
        del ThrCounter

        clear_table('tag')
        fill_table()
        time.sleep(1)
    if stop_event.is_set():
        dpg.set_value(stat, f"scan status: Finished")


def asemble_scan():
    global stop_event
    global test
    ThrAsemble = threading.Thread(target=scanner)
    dpg.set_value(stat, f"scan status: Scanning")
    stop_event.clear()
    test.clear()
    ThrAsemble.start()
    if stop_event.is_set():
        ThrAsemble.join()


with dpg.window(label="Main", id='main_window', width=600, height=600):
    with dpg.menu_bar(label="TopBar"):
        with dpg.group(horizontal=True, horizontal_spacing=7):
            dpg.add_button(label="start", callback=asemble_scan)
            dpg.add_button(label="suspend", callback=change_flag)
            dpg.add_button(label="clear", callback=clear_from_button)
            dpg.add_button(label="save", callback=save)

    with dpg.table(header_row=True, tag='tag', scrollY=True, scrollX=True) as tbl:
        dpg.add_table_column(label="IP")
        dpg.add_table_column(label="MAC")
        dpg.add_table_column(label="Prod")
        dpg.add_table_column(label="Discover time")

    with dpg.child_window(width=600, height=30, border=False,
                          pos=(10, dpg.get_viewport_height() - 75)) as botLabs:
        with dpg.group(horizontal=True, horizontal_spacing=20):
            stat = dpg.add_text("scan status: NoScan")
            sc = dpg.add_text("scanned: 0")
    dpg.set_viewport_resize_callback(lambda: dpg.set_item_pos(botLabs, (10, dpg.get_viewport_height() - 60)))

dpg.set_primary_window("main_window", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
