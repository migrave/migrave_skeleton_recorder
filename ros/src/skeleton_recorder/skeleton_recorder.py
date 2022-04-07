import rospy
import datetime
from pathlib import Path
import pandas as pd


class SkeletonRecorder:
    def __init__(
        self,
        out_directory="skeletons",
    ):

        self._out_directory = out_directory
        self._out_file_path = None

        self._is_recording = False
        self._skeletons = []
        self._timestamps = []

    def start_recording(self, out_file_name=None):

        if self._is_recording:
            raise RuntimeError("Skeleton is already being recorded")

        # parameter set by migrave_games
        parameter_name = "/migrave/game_performance/participant_id"
        if rospy.has_param(parameter_name):
            participant_id = rospy.get_param(parameter_name)
            if participant_id == "":
                rospy.loginfo("Participant ID not set!")
                participant_id = "ID_Unknown"
        else:
            participant_id = "ID_Unknown"

        self._out_directory_id = Path(self._out_directory) / participant_id
        if not Path(self._out_directory_id).is_dir():
            Path(self._out_directory_id).mkdir(parents=True, exist_ok=True)
        if out_file_name is None:
            ext = "csv"
            now = datetime.datetime.now()
            # time in YYYY-MM-DD_HH_MM-SS format
            time = now.strftime("%Y-%m-%d_%H-%M-%S")
            # unixtimestamp 16 digits
            stamp = int(datetime.datetime.timestamp(now) * 1000000)
            file_name = f"{time}_{stamp}"
            out_file_name = f"{file_name}.{ext}"

        out_file_path = Path(self._out_directory_id) / out_file_name
        # out_file_path = str(out_file_path)
        self._out_file_path = out_file_path

        self._is_recording = True

    def add_skeleton(self, skeleton, is_throw_error_if_not_recording=True):

        if self._is_recording:
            now = datetime.datetime.now()
            # unixtimestamp 16 digits
            timestamp = int(datetime.datetime.timestamp(now) * 1000000)
            self._timestamps.append(timestamp)
            self._skeletons.append(skeleton)
        else:
            if is_throw_error_if_not_recording:
                raise RuntimeError("Skeleton recording has not been started")

    def stop_recording(self):

        if not self._is_recording:
            raise RuntimeError("Skeleton recording was not started")

        self._is_recording = False

        df_skeletons = pd.DataFrame(
            {"timestamp": self._timestamps, "skeleton": self._skeletons}
        )
        df_skeletons.to_csv(self._out_file_path, index=False)
