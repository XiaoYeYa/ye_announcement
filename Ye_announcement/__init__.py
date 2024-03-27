from datetime import datetime
import json
from mcdreforged.api.all import *


announcements_file = 'config\\announcements.json'
announcements = []

def load_announcements():
    global announcements
    try:
        with open(announcements_file, 'r') as file:
            announcements = json.load(file)
    except FileNotFoundError:
        announcements = []

def save_announcements():
    with open(announcements_file, 'w') as file:
        json.dump(announcements, file, indent=4)

def send_announcement(server, message, color="white"):
    server.execute('tellraw @a [{"text":"[公告] ","color":"gold"},{"text":"%s","color":"%s"}]' % (message, color))

def on_player_joined(server, player, info):
    for announcement in announcements:
        time, publisher, content, color = announcement
        server.execute('tellraw %s [{"text":"[YE-公告]","color":"dark_red"},{"text":"\\n发布时间：","color":"gray"},{"text":"%s","color":"aqua"},{"text":"\\n发布人：","color":"gray"},{"text":"%s","color":"aqua"},{"text":"\\n内容：","color":"gray"},{"text":"%s","color":"%s"}]' % (player, time, publisher, content, color))

def on_load(server, old_module):
    load_announcements()
    server.register_help_message('!!g <公告内容>', '发布一个公告，只有服主权限可以使用')
    server.register_help_message('!!gd <序号>', '删除指定序号的公告，只有服主权限可以使用')
    server.register_help_message('!!gc <序号> <颜色>', '修改指定序号的公告颜色，只有服主权限可以使用')
    server.register_help_message('!!glist', '显示当前所有的公告信息')
    server.register_help_message('!!ghelp', '获取插件的使用教程和所有的命令')

def on_info(server, info):
    if info.content.startswith('!!g '):
        if not server.get_permission_level(info.player) == 4:
            server.reply(info, '只有服主权限可以发布公告！')
            return
        content = info.content[4:]
        publisher = info.player
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        announcements.append((time, publisher, content, "white"))
        save_announcements()
        send_announcement(server, '夜之粉公告已发布：%s' % content)
    elif info.content.startswith('!!gd '):
        if not server.get_permission_level(info.player) == 4:
            server.reply(info, '只有服主权限可以删除公告！')
            return
        try:
            index = int(info.content[5:]) - 1
            if index < 0 or index >= len(announcements):
                server.reply(info, '序号不存在！')
                return
            del announcements[index]
            save_announcements()
            send_announcement(server, '已删除指定序号的公告', "green")
        except ValueError:
            server.reply(info, '请输入正确的序号！')
    elif info.content.startswith('!!gc '):
        if not server.get_permission_level(info.player) == 4:
            server.reply(info, '只有服主权限可以更改公告颜色！')
            return
        try:
            index, color = info.content[5:].split(' ')
            index = int(index) - 1
            if index < 0 or index >= len(announcements):
                server.reply(info, '序号不存在！')
                return
            announcements[index] = (announcements[index][0], announcements[index][1], announcements[index][2], color)
            save_announcements()
            send_announcement(server, '已更改指定序号的公告颜色为%s' % color, color)
        except ValueError:
            server.reply(info, '请输入正确的序号和颜色！')
    elif info.content.startswith('!!ghelp'):
        server.reply(info, '[夜之粉公告插件帮助]\n§e使用 !!g <公告内容> 发布一个公告\n§e使用 !!gd <序号> 删除指定序号的公告\n§e使用 !!gc <序号> <颜色> 修改指定序号的公告颜色\n§e使用 !!glist 显示所有公告信息，包括序号')
    elif info.content.startswith('!!glist'):
        announcements_list = '\n'.join([f'{i+1}: {announcement[2]}' for i, announcement in enumerate(announcements)])
        server.reply(info, '[夜之粉公告列表]\n§a' + announcements_list)
