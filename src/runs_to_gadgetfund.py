import os
import rollbar
from typing import List

from services.parameter import ParameterService
from services.monetizer import RunsToMoney

from managers.endomondo import Endomondo
from managers.s3 import S3Manager

from models.workout import Run

RUNS_BUCKET_NAME = os.environ.get('RUNS_BUCKET')
PARAMETER_SERVICE = ParameterService()

# rollbar_key = PARAMETER_SERVICE.get('/rollbar/key')
# rollbar.init(rollbar_key, 'runs-to-gadgetfund')

# @rollbar.lambda_function
def handler(event, context):
    s3_manager = S3Manager(RUNS_BUCKET_NAME, 'runs.csv', Run)
    endomondo = Endomondo()
    runs_to_money = RunsToMoney()
    
    if s3_manager.has_entries_online():
        runs = endomondo.get_runs(5)
        max_id_in_s3 = s3_manager.get_max_int()
    else:
        runs = endomondo.get_runs(1)
        max_id_in_s3 = 0

    runs_to_upload = [r for r in runs if r.get_id() > max_id_in_s3 ]
    if runs_to_upload:
        runs_to_money.pay_out_runs(runs_to_upload)
        s3_manager.append(runs_to_upload)

if __name__ == "__main__":
    handler(None, None)
