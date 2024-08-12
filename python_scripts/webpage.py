from flask import Flask, request, jsonify, render_template, Response
from waitress import serve
import os
def web_interface(setting):
    ##settings_list = settings.get_params()
    ##h_params = settings.get_h_params()
    app = Flask(__name__)
    print(setting.get_params())
    print(setting.get_h_params())
    print(setting.get_ip())
    @app.route("/", methods=['GET', 'POST'])
    def main_window():
        if request.method == 'POST':
            if(request.form.get("command") != None): 
                if(request.form.get("command") == "3" or request.form.get("command") == "4" or request.form.get("delete_row") != "0"):
                    h_list = []
                    for i in range(len(setting.get_h_params())):
                        temp_list = [request.form.get(f"table_{i}_0"), int(request.form.get(f"table_{i}_1")), int(request.form.get(f"table_{i}_2"))]
                        h_list.append(temp_list)
                    
                    if(request.form.get("delete_row") != "0"):
                        h_list.pop(int(request.form.get("delete_row")) - 1)
                    elif(request.form.get("command") == "4"):
                        h_list.append(["", 0, 0])
                    setting.set_h_params(h_list)
                elif(request.form.get("command") == "1"):
                    setting.reset_params()
                elif(request.form.get("command") == "2"):
                    setting.save_params()
            else:
                settings_list = [0 for i in range(12)]
                settings_list[0] = int(request.form.get("smin"))
                settings_list[1] = int(request.form.get("vmin"))
                settings_list[2] = int(request.form.get("smax"))
                settings_list[3] = int(request.form.get("vmax"))
                settings_list[4] = int(request.form.get("Areamin"))
                settings_list[5] = int(request.form.get("Areamax"))
                print(request.form.get("aruco"))
                os.system("v4l2-ctl --set-ctrl=brightness=" + str(int(request.form.get('Exposure'))))
                settings_list[6] = int(request.form.get("Exposure"))
                if(int(request.form.get("Whitebalance")) != 1):
                    os.system("v4l2-ctl --set-ctrl=white_balance_automatic=0")
                    os.system("v4l2-ctl --set-ctrl=white_balance_temperature=" + str(int(request.form.get('Whitebalance'))))
                else:
                    os.system("v4l2-ctl --set-ctrl=white_balance_automatic=1")
                settings_list[7] = int(request.form.get("Whitebalance"))
                os.system("v4l2-ctl --set-ctrl=contrast=" + str(int(request.form.get('Contrast'))))
                settings_list[8] = int(request.form.get("Contrast"))
                settings_list[9] = int(request.form.get("Open"))
                settings_list[10] = int(request.form.get("Close"))
                if(request.form.get("aruco") == "on"):
                    settings_list[11] = 1
                else:
                    settings_list[11] = 0
                setting.set_params(settings_list)
        return render_template("webpage.html", settings=setting.get_params(), h_list = setting.get_h_params(), h_len = len(setting.get_h_params()), ip = setting.get_ip())
    serve(app, host=setting.get_ip(), port=5000)

