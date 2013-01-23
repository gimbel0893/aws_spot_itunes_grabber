import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

import datetime
from boto.ec2.connection import EC2Connection


PRICE = 0.005
AMI_ID = 'ami-1624987f'
INSTANCE_TYPE = 't1.micro'
INSTANCE_ARN = 'arn:aws:iam::614962951171:instance-profile/spot-controller'
USER_DATA = '''
#!/bin/bash

#yum update --assumeyes
yum install --assumeyes git python27 MySQL-python mysql-server mysql-devel python27-devel gcc

mkdir /aws_spot_itunes_grabber
cd /aws_spot_itunes_grabber
git clone https://github.com/gimbel0893/aws_spot_itunes_grabber.git scripts

# virualenv setup
easy_install virtualenv
virtualenv --python=python27 env_spot
virtualenv --python=python27 env_itunes

# spot setup
source env_spot/bin/activate
pip install -r scripts/spot_instance/requirements.txt
deactivate

# itunes setup
source env_itunes/bin/activate
pip install -r scripts/itunes_store/requirements.txt
deactivate

# run itunes
source env_itunes/bin/activate
python scripts/itunes_store/grabber.py
deactivate

# run spot
source env_spot/bin/activate
python scripts/spot_instance/reschedule_and_terminate.py
deactivate
'''

class SpotHandler(object):
    def __init__(self, key=None, secret_key=None):
        super(SpotHandler, self).__init__()
        self.conn = EC2Connection(aws_access_key_id=key,
                                  aws_secret_access_key=secret_key)

    def cancel_all(self):
        log.info('starting cancel_all()')
        try:
            for r in self.conn.get_all_spot_instance_requests():
                if r.state == 'open':
                    log.info('about to cancel spot request {}.'.format(r.id))
                    r.cancel()
                    log.info('canceled')
                else:
                    log.info('spot request {} ignored, state={}.' \
                             .format(r.id, r.state))
        except Exception as e:
            log.info('ERROR: type={}, message={}.'.format(type(e), str(e)))
            raise
        log.info('done with cancel_all()')
        return self

    def reschedule(self):
        log.info('starting reschedule()')
        tomorrow = (datetime.datetime.utcnow() + datetime.timedelta(1)) \
                   .isoformat()
        log.info('going to reschedule for {}'.format(tomorrow))
        try:
            req = self.conn.request_spot_instances(PRICE, AMI_ID,
                                valid_from=tomorrow,
                                instance_type=INSTANCE_TYPE,
                                instance_profile_arn=INSTANCE_ARN,
                                user_data=USER_DATA)
            log.info('created spot request {}'.format(req[0].id))
        except Exception as e:
            log.info('ERROR: type={}, message={}.'.format(type(e), str(e)))
            raise
        log.info('done with reschedule()')
        return self

    def terminate_all(self):
        log.info('starting terminate_all()')
        try:
            for i in self.conn.get_all_instances():
                log.info('found instance {}.'.format(i.id))
                if i.instances[0].spot_instance_request_id:
                    log.info('its a spot instance')
                    if i.instances[0].state == 'running':
                        log.info('about to terminate')
                        i.instances[0].terminate()
                        log.info('terminated')
                    else:
                        log.info('instance not running, state={}.' \
                                 .format(i.instances[0].state))
                else:
                    log.info('not a spot instance')
        except Exception as e:
            log.info('ERROR: type={}, message={}.'.format(type(e), str(e)))
            raise
        log.info('done with terminate_all()')
        return self


if __name__ == '__main__':
    handler = SpotHandler()
    handler.cancel_all()
    handler.reschedule()
    handler.terminate_all()
