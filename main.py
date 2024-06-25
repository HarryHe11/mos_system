import random
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
)
import os
import json
from collections import defaultdict
import utils

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloTestMosScore"

MOS_COUNT = 16
USER_MOS_COUNTER = defaultdict(lambda: 1)

tmp_idx_mos = 0
tmp_idx_quality = 0
test_audios = []


idx_list = []


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        return redirect("/login")
    elif request.method == "GET":
        return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        return redirect(url_for("quality_test_index", user=user))
    return render_template("login.html")


@app.route("/<user>/mos_test_example", methods=["GET", "POST"])
def mos_test_example(user):
    if request.method == "POST":
        return redirect(url_for("quality_test_index", user=user))
    elif request.method == "GET":
        return render_template("mos_test_example.html")


@app.route("/<user>/quality_test_index")
def quality_test_index(user):
    return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))

@app.route("/<user>/mos_test_break", methods=["GET", "POST"])
def mos_test_break(user):
    return render_template("mos_test_break.html", user=user)


@app.route("/<user>/mos_test/<int:idx>", methods=["GET", "POST"])
def mos_test(user, idx):
    if idx > USER_MOS_COUNTER[user]:
        return redirect(url_for("mos_test", user=user, idx=USER_MOS_COUNTER[user]))

    if idx == MOS_COUNT + 1:
        return redirect(url_for("mos_test_break", user=user))

    global tmp_idx_mos
    global test_audios

    if tmp_idx_mos < idx:
        test_audios = utils.get_mos_test_audio(type='sim')
        tmp_idx_mos = idx

    print("len ", len(test_audios))
    if request.method == "POST":
        other_test_audios = test_audios[1:]
        rated_systems = []
        for test_audio in other_test_audios:
            system = utils.parse_system_from_audio_path(test_audio)
            rated_systems.append(system)

        rated_time = utils.current_time()

        grades = []
        for i in ['2', '3','4','5']:
            grade = request.form.get("mos{}".format(i))
            grades.append(grade)


        result = []
        for rated_system, test_audio, grade in zip(rated_systems, other_test_audios, grades):
            result.append([rated_system, test_audio, grade])

        res = {
            "type": "sim",
            "time": rated_time,
            "subject": user,
            "subject_test_number": idx,
            "result": result,
        }

        save_dir = "./results/{}".format(user)
        os.makedirs(save_dir, exist_ok=True)
        save_file = os.path.join(save_dir, "{}_sim_{}.json".format(rated_time, user))
        with open(save_file, "w") as f:
            json.dump(res, f, indent=4, ensure_ascii=False)

        print("idx = {}, user_sim_counter = {}".format(idx, USER_MOS_COUNTER[user]))

        if idx == USER_MOS_COUNTER[user]:
            USER_MOS_COUNTER[user] += 1

        return redirect(url_for("mos_test", user=user, idx=USER_MOS_COUNTER[user]))

    return render_template(
        "mos_test.html",
        user=user,
        index=idx,
        wav_file1=test_audios[0],
        wav_file2=test_audios[1],
        wav_file3=test_audios[2],
        wav_file4=test_audios[3],
        wav_file5=test_audios[4],
    )



@app.route("/<user>/quality_test_break", methods=["GET", "POST"])
def quality_test_break(user):
    if request.method == "POST":
        USER_MOS_COUNTER[user] = 1
        return redirect(url_for("mos_test", user=user, idx=USER_MOS_COUNTER[user]))
    elif request.method == "GET":
        return render_template("quality_test_break.html", user=user)

@app.route("/<user>/quality_test/<int:idx>", methods=["GET", "POST"])
def quality_test(user, idx):
    # 如果当前索引大于用户的最大索引，重定向到用户的最大索引页面
    if idx > USER_MOS_COUNTER[user]:
        return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))

    # 如果索引等于总测试数+1，重定向到休息页面
    if idx > MOS_COUNT:
        return redirect(url_for("quality_test_break", user=user))

    global tmp_idx_quality
    global test_audios

    # 更新临时索引并获取新的测试音频
    if tmp_idx_quality < idx:
        print("usr", user)
        test_audios = utils.get_mos_test_audio(type='quality') # CMOS需要完全相同的音频
        tmp_idx_quality = idx

    # 处理POST请求
    if request.method == "POST":
        other_test_audios = test_audios[1:]
        rated_systems = []
        for test_audio in other_test_audios:
            system = utils.parse_system_from_audio_path(test_audio)
            rated_systems.append(system)

        rated_time = utils.current_time()

        # 获取CMOS评分
        grades = []
        for i in ['2', '3','4','5']:
            grade = request.form.get("cmos{}".format(i))
            grades.append(grade)

        # 生成结果
        result = []
        for rated_system, test_audio, grade in zip(rated_systems, other_test_audios, grades):
            result.append([rated_system, test_audio, grade])

        res = {
            "type": "quality",
            "time": rated_time,
            "subject": user,
            "subject_test_number": idx,
            "result": result,
        }
        
        # 保存结果为JSON文件
        save_dir = "./results/{}".format(user)
        os.makedirs(save_dir, exist_ok=True)
        save_file = os.path.join(save_dir, "{}_quality_{}.json".format(rated_time, user))
        with open(save_file, "w") as f:
            json.dump(res, f, indent=4, ensure_ascii=False)
        print("idx = {}, user_quality_counter = {}".format(idx, USER_MOS_COUNTER[user]))

        # 更新用户的最大索引
        if idx == USER_MOS_COUNTER[user]:
            USER_MOS_COUNTER[user] += 1

        return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))

    # 渲染模板并返回页面
    return render_template(
        "quality_test.html",
        user=user,
        index=idx,
        wav_file1=test_audios[0],
        wav_file2=test_audios[1],
        wav_file3=test_audios[2],
        wav_file4=test_audios[3],
        wav_file5=test_audios[4],
    )


if __name__ == "__main__":
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=80)