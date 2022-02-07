from win10toast import ToastNotifier
from pythonping import ping
from infi.systray import SysTrayIcon
from PIL import Image, ImageDraw,ImageFont
from paramiko import SSHClient
import time
import socket

hostname = '1.1.1.1'

pings_per_cycle = 5
drop_count = 0

client = SSHClient()
client.load_system_host_keys()
client.connect('10.0.0.53', username='ubuntu', password='password')

local_machine = socket.gethostname()

i = 1

while True:
    current_time = int(time.time())
    try: 
        response = ping(hostname,timeout=1, size=1, count=pings_per_cycle, verbose=False,interval=2)
        formatted_response = "{:.0f}".format(response.rtt_avg_ms)

        # init the notification object and sets conditions in which it is triggered
        notify = ToastNotifier()
        if response.success() == False:
                print('timeout')
                notify.show_toast('Connection Alert', 'Connection to {} is down'.format(hostname))
                drop_count += 1
        else:
            print(current_time, int(response.rtt_avg_ms))

    # catch Windows errors and notifies user
    except OSError as error: 
            notify.show_toast('Connection Alert', 'Connection to {} is down'.format(hostname))
            print(error)
            drop_count += 1 
    
    local_path = '' + local_machine + '.csv'
    remote_path = '/home/ubuntu/net-log/' + local_machine + '.csv'
    sftp_client = client.open_sftp()
    
    try: 
        sftp_client.stat(remote_path)
        client.exec_command('echo ' + str(current_time) + ',' + str(int(response.rtt_avg_ms)) + ' >> /home/ubuntu/net-log/' + local_machine + '.csv')
    except IOError:
        client.exec_command('echo date,latency >> /home/ubuntu/net-log/' + local_machine + '.csv')
        client.exec_command('echo ' + str(current_time) + ',' + str(int(response.rtt_avg_ms)) + ' >> /home/ubuntu/net-log/' + local_machine + '.csv')
        
    # init transparent image
    img = Image.new('RGBA', (50, 50), color = (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (50, 50)], fill=(255, 255, 255, 0), outline=None)

     # scale text size based on number of characters
    if len(formatted_response) <= 2:
        font_size = 45
        padding = (5,5)
    elif len(formatted_response) >= 4:
        font_size = 30
        padding = (0,5)
    else:
        font_size = 32
        padding = (0,10)

    # add text to image
    image = "systray.ico"
    font_type  = ImageFont.truetype('calibrib.ttf', font_size)
    d.text((padding), formatted_response, fill=(255,255,255), font = font_type)
    img.save(image)
    
    # display image in systray 
    formatted_hover_text = formatted_response + ' ms to ' + hostname
    
    if i == 1:
        total_pings = pings_per_cycle
        systray = SysTrayIcon(image, hover_text = formatted_hover_text + '\n' + str(drop_count) + ' connection drops today.' + '\n' + str(total_pings) + ' total pings sent')
        systray.start()
    else:
        total_pings = i * pings_per_cycle
        systray.update(icon=image, hover_text = formatted_hover_text +  '\n' +  str(drop_count) +  ' connection drops today.' + '\n' + str(total_pings) + ' total pings sent')
    i += 1
     
    






