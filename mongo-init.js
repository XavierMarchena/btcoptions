function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

conn = new Mongo();
db = conn.getDB("admin");
db.createUser(
  {
    user: "btcoptions_user",
    pwd: "Kh0qsAoltzz", // or cleartext password
     roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
  }
);
conn = new Mongo();
db = conn.getDB("btcoptions");
//Nice GUID: ballades-sloe-lace-blee-calflesscoff

db.platforms.insert({"platform_id": "ba11ade5-510e-1ace-b1ee-ca1f1e55c0ff","hostname": "casino.rgtslots.com", "getbalance_url": "https://casino.rgtslots.com/getbalance",
"setbet_url": "https://casino.rgtslots.com/setbet", "developer_id": "1", "key": "4N8y5bZQPFL9", "casino_home_url": "cryptobet.com",
"client_id":"1", "idgame":"1", "configuration":'{"bet_multiplier":1.5, "bet_min":1, "bet_max":100}'})

db.btc_range.createIndex( { "date": 1 }, { expireAfterSeconds: 86400 } );
//{"_id":{"$oid":"6035dfafdd895b97a783b695"},"platform_id":"c8fbc2c8-335c-4134-b751-371b3008b7bc","hostname":"casino.rgtslots.com","getbalance_url":"http://192.168.99.102:8080/getbalance","setbet_url":"http://192.168.99.102:8080/setbet","developer_id":"1","key":"4N8y5bZQPFL9","casino_home_url":"cryptobet.com","client_id":"1","idgame":"12","configuration":"{\"bet_multiplier\":1.5, \"bet_min\":1, \"bet_max\":100}"}
