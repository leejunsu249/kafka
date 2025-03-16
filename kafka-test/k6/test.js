import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  vus: 1000,       // 동시 가상 유저 수
  duration: '3m', // 테스트 지속 시간
};

export default function () {
  const res = http.get('http://localhost:30080/produce');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
