from datetime import datetime
import json
from mcdreforged.api.all import *

announcements_file = 'config\\announcements.json'
announcements = []
server_name = '夜之粉'

def load_announcements():
    global announcements, server_name
    try:
        with open(announcements_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            announcements = data.get('announcements', [])
            server_name = data.get('server_name', '夜之粉')
    except FileNotFoundError:
        announcements = []
        server_name = '夜之粉'

def save_announcements():
    with open(announcements_file, 'w', encoding='utf-8') as file:
        json.dump({'announcements': announcements, 'server_name': server_name}, file, indent=4, ensure_ascii=False)

def send_announcement(server, message, color="white"):
    server.execute('tellraw @a [{"text":"[%s] ","color":"gold"},{"text":"%s","color":"%s"}]' % (server_name, message, color))

def on_player_joined(server, player, info):
    for announcement in announcements:
        time, publisher, content, color = announcement
        server.execute('tellraw %s [{"text":"======= ","color":"white"},{"text":"[%s-公告]","color":"yellow"},{"text":" =======","color":"white"},{"text":"\\n发布时间：","color":"gray"},{"text":"%s","color":"aqua"},{"text":"\\n发布人：","color":"gray"},{"text":"%s","color":"aqua"},{"text":"\\n内容：","color":"gray"},{"text":"%s","color":"%s"},{"text":"\\n-------------","color":"white"}]' % (player, server_name, time, publisher, content, color))

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
            server.reply(info, '§c只有服主权限可以发布公告！')
            return
        content = info.content[4:]
        publisher = info.player
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        announcements.append((time, publisher, content, "white"))
        save_announcements()
        send_announcement(server, '%s公告已发布：%s' % (server_name, content))
    elif info.content.startswith('!!gd '):
        if not server.get_permission_level(info.player) == 4:
            server.reply(info, '§c只有服主权限可以删除公告！')
            return
        try:
            index = int(info.content[5:]) - 1
            if index < 0 or index >= len(announcements):
                server.reply(info, '§c序号不存在！§a如果您不知道公告序号，请使用!!glist来查看所有公告序号。')
                return
            del announcements[index]
            save_announcements()
            send_announcement(server, '已删除指定序号的公告', "green")
        except ValueError:
            server.reply(info, '§c请输入§a正确§c的序号！')
    elif info.content.startswith('!!gc '):
        if not server.get_permission_level(info.player) == 4:
            server.reply(info, '§c只有服主权限可以更改公告颜色！')
            return
        try:
            index, color = info.content[5:].split(' ')
            index = int(index) - 1
            if index < 0 or index >= len(announcements):
                server.reply(info, '§c序号不存在！§a如果您不知道公告序号，请使用!!glist来查看所有公告序号。')
                return
            announcements[index] = (announcements[index][0], announcements[index][1], announcements[index][2], color)
            save_announcements()
            send_announcement(server, '已更改指定序号的公告颜色为%s' % color, color)
        except ValueError:
            server.reply(info, '§c请输入正确的序号和颜色！')
    elif info.content.startswith('!!ghelp'):
        server.reply(info, '[%s公告插件帮助]\n§e使用 !!g <公告内容> 发布一个公告\n§e使用 !!gd <序号> 删除指定序号的公告\n§e使用 !!gc <序号> <颜色> 修改指定序号的公告颜色\n§e使用 !!glist 显示所有公告信息，包括序号\n§e使用 !!gr 重载配置文件' % server_name)
    elif info.content.startswith('!!glist'):
        announcements_list = '\n'.join([f'{i+1}: {announcement[2]}' for i, announcement in enumerate(announcements)])
        server.reply(info, '[%s公告列表]\n§a' % server_name + announcements_list)
    elif info.content.startswith('!!gr'):
        if server.get_permission_level(info.player) != 4:
            server.reply(info, '§c只有服主权限可以重载配置文件！')
            return
        load_announcements()
        server.reply(info, '§a配置文件已重新加载！')
