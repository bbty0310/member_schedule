import pandas as pd

class ExportManager:
    @staticmethod
    def export_to_excel(schedule, file_name="schedule.xlsx"):
        data = []
        for entry in schedule:
            data.append({"직원 이름": entry[1], "요일": entry[2], "시간": entry[3]})
        df = pd.DataFrame(data)
        df.to_excel(file_name, index=False)
        print(f"스케줄이 {file_name}에 저장되었습니다.")