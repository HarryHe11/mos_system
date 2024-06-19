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

MOS_COUNT = 10
# AB_COUNT = 18
USER_MOS_COUNTER = defaultdict(lambda: 1)
# USER_AB_COUNTER = defaultdict(lambda: 1)

tmp_idx_mos = 0
tmp_idx_quality = 0
test_audios = []

# tmp_idx_preference = 0
# preference_audios = []

idx_list = []


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        return redirect("/login")
    elif request.method == "GET":
        return render_template("home.html")


# @app.route("/<user>/tutorial", methods=["GET", "POST"])
# def tutorial(user):
#     if request.method == "POST":
#         return redirect(url_for("mos_test_example", user=user))
#     elif request.method == "GET":
#         return render_template("tutorial.html")


# @app.route("/<user>/aliasing", methods=["GET", "POST"])
# def aliasing(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("aliasing.html")


# @app.route("/<user>/frequency", methods=["GET", "POST"])
# def frequency(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("frequency.html")


# @app.route("/<user>/pitch", methods=["GET", "POST"])
# def pitch(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("pitch.html")


# @app.route("/<user>/periodicity", methods=["GET", "POST"])
# def periodicity(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("periodicity.html")


# @app.route("/<user>/click", methods=["GET", "POST"])
# def click(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("click.html")


# @app.route("/<user>/metallic", methods=["GET", "POST"])
# def metallic(user):
#     if request.method == "POST":
#         return redirect(url_for("tutorial", user=user))
#     elif request.method == "GET":
#         return render_template("metallic.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        return redirect(url_for("mos_test_example", user=user))
    return render_template("login.html")


@app.route("/<user>/mos_test_example", methods=["GET", "POST"])
def mos_test_example(user):
    if request.method == "POST":
        return redirect(url_for("mos_test_index", user=user))
    elif request.method == "GET":
        return render_template("mos_test_example.html")


@app.route("/<user>/mos_test_index")
def mos_test_index(user):
    return redirect(url_for("mos_test", user=user, idx=USER_MOS_COUNTER[user]))


@app.route("/<user>/mos_test_break", methods=["GET", "POST"])
def mos_test_break(user):
    if request.method == "POST":
        USER_MOS_COUNTER[user] = 1
        return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))
    elif request.method == "GET":
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

    if request.method == "POST":
        other_test_audios = [test_audios[1], test_audios[2], test_audios[4], test_audios[5]]
        rated_systems = []
        for test_audio in other_test_audios:
            system = utils.parse_system_from_audio_path(test_audio)
            rated_systems.append(system)

        rated_time = utils.current_time()

        grades = []
        for i in ['2', '3', '5', '6']:
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
        wav_file6=test_audios[5],
    )

@app.route("/<user>/quality_test_break", methods=["GET", "POST"])
def quality_test_break(user):
    return render_template("quality_test_break.html", user=user)

@app.route("/<user>/quality_test/<int:idx>", methods=["GET", "POST"])
def quality_test(user, idx):
    if idx > USER_MOS_COUNTER[user]:
        return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))

    if idx == MOS_COUNT + 1:
        return redirect(url_for("quality_test_break", user=user))

    global tmp_idx_quality
    global test_audios

    if tmp_idx_quality < idx:
        test_audios = utils.get_mos_test_audio(type='quality')
        tmp_idx_quality = idx

    if request.method == "POST":
        other_test_audios = test_audios
        rated_systems = []
        for test_audio in other_test_audios:
            system = utils.parse_system_from_audio_path(test_audio)
            rated_systems.append(system)

        rated_time = utils.current_time()

        grades = []
        for i in range(1, len(test_audios) + 1):
            grade = request.form.get("mos{}".format(i))
            grades.append(grade)


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

        save_dir = "./results/{}".format(user)
        os.makedirs(save_dir, exist_ok=True)
        save_file = os.path.join(save_dir, "{}_quality_{}.json".format(rated_time, user))
        with open(save_file, "w") as f:
            json.dump(res, f, indent=4, ensure_ascii=False)

        print("idx = {}, user_quality_counter = {}".format(idx, USER_MOS_COUNTER[user]))

        if idx == USER_MOS_COUNTER[user]:
            USER_MOS_COUNTER[user] += 1

        return redirect(url_for("quality_test", user=user, idx=USER_MOS_COUNTER[user]))

    return render_template(
        "quality_test.html",
        user=user,
        index=idx,
        wav_file1=test_audios[0],
        wav_file2=test_audios[1],
        wav_file3=test_audios[2],
        wav_file4=test_audios[3],
        # wav_file5=test_audios[4],
        # wav_file6=test_audios[5],
    )

# @app.route("/<user>/preference_example", methods=["GET", "POST"])
# def preference_example(user):
#     if request.method == "POST":
#         idx_list_1 = [i for i in range(AB_COUNT // 2)]
#         idx_list_2 = [i for i in range(AB_COUNT // 2)]
#         random.shuffle(idx_list_1)
#         random.shuffle(idx_list_2)

#         global idx_list
#         idx_list = idx_list_1 + idx_list_2
#         return redirect(
#             url_for(
#                 "preference_index",
#                 user=user,
#             ),
#         )
#     elif request.method == "GET":
#         return render_template("preference_example.html")


# @app.route("/<user>/preference_index")
# def preference_index(user):
#     return redirect(
#         url_for(
#             "preference",
#             user=user,
#             idx=USER_AB_COUNTER[user],
#         )
#     )


# @app.route("/<user>/preference_break", methods=["GET", "POST"])
# def preference_break(user):
#     return render_template("preference_break.html", user=user)


# @app.route("/<user>/preference/<int:idx>", methods=["GET", "POST"])
# def preference(user, idx):
#     if idx > USER_AB_COUNTER[user]:
#         return redirect(
#             url_for(
#                 "preference",
#                 user=user,
#                 idx=USER_AB_COUNTER[user],
#             )
#         )

#     if idx == AB_COUNT + 1:
#         return redirect(url_for("preference_break", user=user))

#     if idx <= 9:
#         seen_unseen = "seen"
#     else:
#         seen_unseen = "unseen"

#     global tmp_idx_preference
#     global preference_audios
#     global idx_list

#     if tmp_idx_preference < idx:
#         index = idx_list[idx - 1] % 3

#         preference_audios = utils.get_preference_test_audio(seen_unseen, index)
#         tmp_idx_preference = idx

#     if request.method == "POST":
#         rated_systems = []
#         for preference_audio in preference_audios:
#             system = utils.parse_system_from_audio_path(preference_audio)
#             rated_systems.append(system)

#         rated_time = utils.current_time()

#         grade = request.form.get("preference")

#         result = []
#         for rated_system, preference_audio in zip(rated_systems, preference_audios):
#             result.append([rated_system, preference_audio])

#         res = {
#             "type": "preference",
#             "time": rated_time,
#             "subject": user,
#             "subject_test_number": idx,
#             "grade": grade,
#             "result": result,
#         }

#         save_dir = "./results/{}".format(user)
#         os.makedirs(save_dir, exist_ok=True)
#         save_file = os.path.join(
#             save_dir, "{}_preference_{}.json".format(rated_time, user)
#         )
#         with open(save_file, "w") as f:
#             json.dump(res, f, indent=4, ensure_ascii=False)

#         print(
#             "idx = {}, user_preference_counter = {}".format(idx, USER_AB_COUNTER[user])
#         )

#         if idx == USER_AB_COUNTER[user]:
#             USER_AB_COUNTER[user] += 1

#         return redirect(
#             url_for(
#                 "preference",
#                 user=user,
#                 idx=USER_AB_COUNTER[user],
#             )
#         )

#     return render_template(
#         "preference.html",
#         user=user,
#         index=idx,
#         wav_file_1=preference_audios[0],
#         wav_file_2=preference_audios[1],
#         wav_file_gt=preference_audios[2],
#     )


# @app.route("/<user>/quality_example", methods=["GET", "POST"])
# def quality_example(user):
#     if request.method == "POST":
#         return redirect(url_for("quality_index", user=user))
#     else:
#         return render_template(
#             "quality_example.html",
#             wav_file1="static/data/gt/IDF1/10059.wav",
#             wav_file2="static/data/fastsvc/SF1/CDF1/30001.wav",
#         )


# @app.route("/<user>/similarity_example", methods=["GET", "POST"])
# def similarity_example(user):
#     if request.method == "POST":
#         return redirect(url_for("similarity_index", user=user))
#     else:
#         return render_template(
#             "similarity_example.html",
#             wav_file1="static/data/gt/IDF1/10059.wav",
#             wav_file2="static/data/gt/IDF1/10001.wav",
#             wav_file3="static/data/fastsvc/SM1/CDM1/30007.wav",
#             wav_file4="static/data/gt/CDM1/10014.wav",
#         )


# @app.route("/<user>/similarity")
# def similarity_index(user):
#     return redirect(
#         url_for("similarity_test", user=user, idx=USER_SIMILARITY_COUNTER[user])
#     )


# @app.route("/<user>/similarity/<int:idx>", methods=["GET", "POST"])
# def similarity_test(user, idx):
#     if idx > USER_SIMILARITY_COUNTER[user]:
#         return redirect(
#             url_for("similarity_test", user=user, idx=USER_SIMILARITY_COUNTER[user])
#         )

#     if idx == SIMILARITY_COUNT + 1:
#         # The similarity part is done.
#         return render_template("similarity_break.html", user=user)

#     # Pick two audios (wish same speaker) randomly
#     rated_files_pair = USER_SIMILARITY_RECORED[user][idx]
#     if len(rated_files_pair) == 0:
#         # ref_file = utils.random_choose_a_gt_audio()
#         # ref_speaker = utils.parse_speaker_from_audio_path(ref_file)

#         # # The rated file can be from both gt or machine generated.
#         # rated_file = utils.random_choose_an_audio()
#         # while utils.parse_speaker_from_audio_path(rated_file) != ref_speaker:
#         #     rated_file = utils.random_choose_an_audio()

#         rated_files_pair = utils.get_similarity_test_audio(
#             user.split("#")[-1], SAMPLE_ORDER[idx - 1]
#         )
#         USER_SIMILARITY_RECORED[user][idx] = rated_files_pair

#     if request.method == "POST":
#         ref_file, rated_file = rated_files_pair
#         rated_system = utils.parse_system_from_audio_path(rated_file)
#         rated_time = utils.current_time()
#         grade = int(request.form.get("similarity"))

#         res = {
#             "type": "similarity",
#             "system": rated_system,
#             "time": rated_time,
#             "subject": user,
#             "subject_test_number": idx,
#             "reference_file": ref_file,
#             "rated_file": rated_file,
#             "grade": grade,
#         }

#         save_dir = "./results/{}".format(user)
#         os.makedirs(save_dir, exist_ok=True)
#         save_file = os.path.join(
#             save_dir, "{}_similarity_{}.json".format(rated_time, rated_system, user)
#         )
#         with open(save_file, "w") as f:
#             json.dump(res, f, indent=4, ensure_ascii=False)

#         print(
#             "idx = {}, user_similarity_counter = {}".format(
#                 idx, USER_SIMILARITY_COUNTER[user]
#             )
#         )

#         if idx == USER_SIMILARITY_COUNTER[user]:
#             USER_SIMILARITY_COUNTER[user] += 1

#         return redirect(
#             url_for("similarity_test", user=user, idx=USER_SIMILARITY_COUNTER[user])
#         )

#     # Shuffle the two-audio pair
#     wav_file_1, wav_file_2 = random.sample(rated_files_pair, 2)

#     return render_template(
#         "similarity.html",
#         user=user,
#         index=idx,
#         wav_file_1=wav_file_1,
#         wav_file_2=wav_file_2,
#     )


if __name__ == "__main__":
    # app.run(host="10.26.1.188", debug=True, port="3232")
    # app.run(debug=True)

    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=5000)
