// app/index.tsx
// Fire Alarm System - Expo Router version
// Chạy được ngay bằng mock data, chưa cần Firebase.

import { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Animated,
  FlatList,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

type SystemStatus = 'safe' | 'warning' | 'fire' | 'offline' | 'battery' | 'buzzer_on' | 'buzzer_off';

type AlertHistory = {
  id: string;
  time: string;
  message: string;
  status: SystemStatus;
  smoke: number;
  battery: number;
  energy: number;
};

type DeviceData = {
  id: string;
  name: string;
  location: string;
  smoke: number;
  battery: number;
  energy: number;
  buzzer: boolean;
  online: boolean;
  updatedAt: string;
};

const SMOKE_WARNING_THRESHOLD = 60;
const SMOKE_FIRE_THRESHOLD = 80;
const BATTERY_LOW_THRESHOLD = 20;

const initialDevice: DeviceData = {
  id: 'device01',
  name: 'Fire Sensor 01',
  location: 'Phòng Lab',
  smoke: 42,
  battery: 85,
  energy: 1.25,
  buzzer: false,
  online: true,
  updatedAt: new Date().toLocaleTimeString('vi-VN'),
};

const initialHistory: AlertHistory[] = [
  {
    id: '1',
    time: '14:30',
    message: 'Cảnh báo cháy: khói vượt ngưỡng nguy hiểm',
    status: 'fire',
    smoke: 88,
    battery: 84,
    energy: 1.31,
  },
  {
    id: '2',
    time: '11:15',
    message: 'Khói vượt ngưỡng cảnh báo',
    status: 'warning',
    smoke: 66,
    battery: 85,
    energy: 1.27,
  },
  {
    id: '3',
    time: '09:20',
    message: 'Hệ thống hoạt động bình thường',
    status: 'safe',
    smoke: 38,
    battery: 86,
    energy: 1.21,
  },
];

function getStatus(device: DeviceData) {
  if (!device.online) {
    return {
      label: 'OFFLINE',
      message: 'Thiết bị đang mất kết nối',
      icon: '📡',
      color: '#a4b0be',
      background: '#747d8c20',
    };
  }

  if (device.smoke >= SMOKE_FIRE_THRESHOLD) {
    return {
      label: 'CẢNH BÁO CHÁY',
      message: 'Khói vượt ngưỡng nguy hiểm, cần kiểm tra ngay',
      icon: '🚨',
      color: '#ff4757',
      background: '#ff475720',
    };
  }

  if (device.smoke >= SMOKE_WARNING_THRESHOLD) {
    return {
      label: 'CẢNH BÁO KHÓI',
      message: 'Nồng độ khói đang tăng cao',
      icon: '⚠️',
      color: '#ffa502',
      background: '#ffa50220',
    };
  }

  if (device.battery <= BATTERY_LOW_THRESHOLD) {
    return {
      label: 'PIN YẾU',
      message: 'Pin thiết bị thấp, cần sạc hoặc thay pin',
      icon: '🪫',
      color: '#ffa502',
      background: '#ffa50220',
    };
  }

  return {
    label: 'AN TOÀN',
    message: 'Tất cả hệ thống đang hoạt động ổn định',
    icon: '✅',
    color: '#2ed573',
    background: '#2ed57320',
  };
}

function getBatteryIcon(battery: number) {
  if (battery > 60) return '🔋';
  if (battery > 20) return '🪫';
  return '⚡';
}

function getHistoryColor(status: SystemStatus) {
  if (status === 'fire') return '#ff4757';
  if (status === 'warning' || status === 'battery') return '#ffa502';
  if (status === 'offline') return '#a4b0be';
  if (status === 'buzzer_on') return '#ff4757';
  return '#2ed573';
}

function SensorCard({
  title,
  value,
  danger,
  icon,
  subtitle,
  color,
}: {
  title: string;
  value: string;
  danger: boolean;
  icon: string;
  subtitle?: string;
  color: string;
}) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    let loop: Animated.CompositeAnimation | null = null;

    if (danger) {
      loop = Animated.loop(
        Animated.sequence([
          Animated.timing(scaleAnim, { toValue: 1.05, duration: 400, useNativeDriver: true }),
          Animated.timing(scaleAnim, { toValue: 1, duration: 400, useNativeDriver: true }),
        ])
      );
      loop.start();
    } else {
      scaleAnim.setValue(1);
    }

    return () => loop?.stop();
  }, [danger, scaleAnim]);

  return (
    <Animated.View
      style={[
        styles.card,
        danger && styles.cardDanger,
        { transform: [{ scale: scaleAnim }] },
      ]}
    >
      <Text style={styles.cardIcon}>{icon}</Text>
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={[styles.cardValue, { color }]}>{value}</Text>
      {subtitle && <Text style={styles.cardSubtitle}>{subtitle}</Text>}
      <View style={[styles.cardBadge, { backgroundColor: danger ? '#ff475720' : '#2ed57320' }]}>
        <Text style={{ color: danger ? '#ff4757' : '#2ed573', fontSize: 11, fontWeight: '700' }}>
          {danger ? '⚠ NGUY HIỂM' : '✓ BÌNH THƯỜNG'}
        </Text>
      </View>
    </Animated.View>
  );
}

function MiniBarChart({ title, values, unit }: { title: string; values: number[]; unit: string }) {
  const maxValue = Math.max(...values, 1);

  return (
    <View style={styles.chartBox}>
      <View style={styles.chartHeader}>
        <Text style={styles.chartTitle}>{title}</Text>
        <Text style={styles.chartUnit}>{unit}</Text>
      </View>
      <View style={styles.chartBars}>
        {values.map((value, index) => {
          const height = Math.max(10, (value / maxValue) * 90);
          return (
            <View key={`${title}-${index}`} style={styles.barItem}>
              <View style={[styles.bar, { height }]} />
              <Text style={styles.barLabel}>{index + 1}</Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

export default function HomeScreen() {
  const [device, setDevice] = useState<DeviceData>(initialDevice);
  const [history, setHistory] = useState<AlertHistory[]>(initialHistory);
  const [autoSimulate, setAutoSimulate] = useState(true);
  const [notificationEnabled, setNotificationEnabled] = useState(true);
  const [smokeWarning, setSmokeWarning] = useState(String(SMOKE_WARNING_THRESHOLD));
  const [smokeFire, setSmokeFire] = useState(String(SMOKE_FIRE_THRESHOLD));
  const flashAnim = useRef(new Animated.Value(1)).current;
  const flashLoop = useRef<Animated.CompositeAnimation | null>(null);

  const status = getStatus(device);
  const isDanger = device.smoke >= SMOKE_FIRE_THRESHOLD || !device.online;
  const smokeChartData = history.slice(0, 6).reverse().map((item) => item.smoke);
  const energyChartData = history.slice(0, 6).reverse().map((item) => item.energy);

  useEffect(() => {
    if (!autoSimulate) return;

    const interval = setInterval(() => {
      setDevice((prev) => {
        const nextSmoke = Math.max(0, +(prev.smoke + (Math.random() - 0.45) * 10).toFixed(1));
        const nextBattery = Math.max(0, prev.battery - Math.floor(Math.random() * 2));
        const nextEnergy = +(prev.energy + Math.random() * 0.04).toFixed(2);

        return {
          ...prev,
          smoke: nextSmoke,
          battery: nextBattery,
          energy: nextEnergy,
          updatedAt: new Date().toLocaleTimeString('vi-VN'),
        };
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [autoSimulate]);

  useEffect(() => {
    const newStatus = getStatus(device);

    if (device.smoke >= SMOKE_FIRE_THRESHOLD && notificationEnabled) {
      Alert.alert('CẢNH BÁO CHÁY!', 'Nồng độ khói vượt ngưỡng nguy hiểm. Vui lòng kiểm tra khu vực ngay.');
    }

    if (device.smoke >= SMOKE_WARNING_THRESHOLD || device.battery <= BATTERY_LOW_THRESHOLD || !device.online) {
      const item: AlertHistory = {
        id: Date.now().toString(),
        time: new Date().toLocaleTimeString('vi-VN'),
        message: newStatus.message,
        status:
          device.smoke >= SMOKE_FIRE_THRESHOLD
            ? 'fire'
            : device.smoke >= SMOKE_WARNING_THRESHOLD
              ? 'warning'
              : device.battery <= BATTERY_LOW_THRESHOLD
                ? 'battery'
                : !device.online
                  ? 'offline'
                  : 'safe',
        smoke: device.smoke,
        battery: device.battery,
        energy: device.energy,
      };

      setHistory((prev) => {
        const duplicated = prev[0]?.message === item.message && prev[0]?.smoke === item.smoke;
        if (duplicated) return prev;
        return [item, ...prev].slice(0, 20);
      });
    }
  }, [device.smoke, device.battery, device.online]);

  useEffect(() => {
    if (isDanger) {
      flashLoop.current = Animated.loop(
        Animated.sequence([
          Animated.timing(flashAnim, { toValue: 0.15, duration: 300, useNativeDriver: true }),
          Animated.timing(flashAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
        ])
      );
      flashLoop.current.start();
    } else {
      flashLoop.current?.stop();
      flashAnim.setValue(1);
    }

    return () => flashLoop.current?.stop();
  }, [isDanger, flashAnim]);

  const toggleBuzzer = () => {
    const nextBuzzer = !device.buzzer;
    setDevice((prev) => ({ ...prev, buzzer: nextBuzzer, updatedAt: new Date().toLocaleTimeString('vi-VN') }));

    const item: AlertHistory = {
      id: Date.now().toString(),
      time: new Date().toLocaleTimeString('vi-VN'),
      message: nextBuzzer ? 'Bật còi báo động thủ công' : 'Tắt còi báo động thủ công',
      status: nextBuzzer ? 'buzzer_on' : 'buzzer_off',
      smoke: device.smoke,
      battery: device.battery,
      energy: device.energy,
    };

    setHistory((prev) => [item, ...prev].slice(0, 20));
  };

  const testFire = () => {
    setDevice((prev) => ({
      ...prev,
      smoke: 88,
      buzzer: true,
      updatedAt: new Date().toLocaleTimeString('vi-VN'),
    }));
  };

  const resetSystem = () => {
    setDevice((prev) => ({
      ...prev,
      smoke: 35,
      buzzer: false,
      online: true,
      updatedAt: new Date().toLocaleTimeString('vi-VN'),
    }));
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Animated.Text style={[styles.headerIcon, { opacity: isDanger ? flashAnim : 1 }]}>🔥</Animated.Text>
        <Text style={styles.headerText}>Fire Alarm System</Text>
        <Text style={styles.headerSub}>Giám sát báo cháy realtime</Text>
      </View>

      <Animated.View
        style={[
          styles.statusCard,
          { backgroundColor: status.background, borderColor: status.color },
          isDanger && { opacity: flashAnim },
        ]}
      >
        <Text style={styles.statusIcon}>{status.icon}</Text>
        <View style={{ flex: 1 }}>
          <Text style={[styles.statusTitle, { color: status.color }]}>{status.label}</Text>
          <Text style={styles.statusSub}>{status.message}</Text>
          <Text style={styles.updatedText}>Cập nhật: {device.updatedAt}</Text>
        </View>
      </Animated.View>

      <Text style={styles.sectionTitle}>📡 Thông số hệ thống</Text>
      <View style={styles.row}>
        <SensorCard
          icon="💨"
          title="Khói"
          value={`${device.smoke} ppm`}
          danger={device.smoke >= SMOKE_WARNING_THRESHOLD}
          subtitle={`Cảnh báo: ${SMOKE_WARNING_THRESHOLD} ppm`}
          color={device.smoke >= SMOKE_WARNING_THRESHOLD ? '#ff4757' : '#2ed573'}
        />
        <SensorCard
          icon={getBatteryIcon(device.battery)}
          title="Pin thiết bị"
          value={`${device.battery}%`}
          danger={device.battery <= BATTERY_LOW_THRESHOLD}
          subtitle={`Ngưỡng: ${BATTERY_LOW_THRESHOLD}%`}
          color={device.battery <= BATTERY_LOW_THRESHOLD ? '#ffa502' : '#2ed573'}
        />
      </View>

      <View style={styles.row}>
        <SensorCard
          icon="⚡"
          title="Năng lượng"
          value={`${device.energy} Wh`}
          danger={false}
          subtitle="Tiêu thụ hiện tại"
          color="#70a1ff"
        />
        <SensorCard
          icon="🔔"
          title="Còi báo"
          value={device.buzzer ? 'Đang bật' : 'Đang tắt'}
          danger={device.buzzer}
          subtitle="Điều khiển thủ công"
          color={device.buzzer ? '#ff4757' : '#2ed573'}
        />
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity
          style={[styles.smallButton, device.buzzer ? styles.buttonOff : styles.buttonOn]}
          onPress={toggleBuzzer}
          activeOpacity={0.85}
        >
          <Text style={styles.buttonText}>{device.buzzer ? '🔕 Tắt còi' : '🔔 Bật còi'}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.smallButton, styles.buttonTest]} onPress={testFire} activeOpacity={0.85}>
          <Text style={styles.buttonText}>🚨 Test cháy</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.resetButton} onPress={resetSystem} activeOpacity={0.85}>
        <Text style={styles.resetButtonText}>✅ Reset về trạng thái an toàn</Text>
      </TouchableOpacity>

      <Text style={styles.sectionTitle}>📊 Biểu đồ dữ liệu</Text>
      <MiniBarChart title="Nồng độ khói" values={smokeChartData.length ? smokeChartData : [0, 0, 0, 0, 0, 0]} unit="ppm" />
      <MiniBarChart title="Năng lượng tiêu thụ" values={energyChartData.length ? energyChartData : [0, 0, 0, 0, 0, 0]} unit="Wh" />

      <Text style={styles.sectionTitle}>🧩 Chi tiết thiết bị</Text>
      <View style={styles.infoBox}>
        <InfoRow label="Tên thiết bị" value={device.name} />
        <InfoRow label="Mã thiết bị" value={device.id} />
        <InfoRow label="Vị trí" value={device.location} />
        <InfoRow label="Kết nối" value={device.online ? 'Online' : 'Offline'} />
        <InfoRow label="Còi báo động" value={device.buzzer ? 'Đang bật' : 'Đang tắt'} />
      </View>

      <Text style={styles.sectionTitle}>⚙️ Cài đặt</Text>
      <View style={styles.settingBox}>
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Ngưỡng cảnh báo khói</Text>
          <TextInput
            value={smokeWarning}
            onChangeText={setSmokeWarning}
            keyboardType="numeric"
            style={styles.input}
            placeholder="60"
            placeholderTextColor="#ffffff40"
          />
          <Text style={styles.inputNote}>Bản preview đang dùng ngưỡng cố định trong code: {SMOKE_WARNING_THRESHOLD} ppm</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Ngưỡng cháy nguy hiểm</Text>
          <TextInput
            value={smokeFire}
            onChangeText={setSmokeFire}
            keyboardType="numeric"
            style={styles.input}
            placeholder="80"
            placeholderTextColor="#ffffff40"
          />
          <Text style={styles.inputNote}>Bản Firebase thật có thể cho lưu ngưỡng này lên database.</Text>
        </View>

        <View style={styles.switchRow}>
          <View>
            <Text style={styles.inputLabel}>Thông báo cảnh báo</Text>
            <Text style={styles.inputNote}>Hiện popup khi khói vượt ngưỡng cháy</Text>
          </View>
          <Switch value={notificationEnabled} onValueChange={setNotificationEnabled} />
        </View>

        <View style={styles.switchRow}>
          <View>
            <Text style={styles.inputLabel}>Tự mô phỏng dữ liệu</Text>
            <Text style={styles.inputNote}>Tự thay đổi khói, pin, năng lượng mỗi 5 giây</Text>
          </View>
          <Switch value={autoSimulate} onValueChange={setAutoSimulate} />
        </View>
      </View>

      <Text style={styles.sectionTitle}>🕐 Lịch sử cảnh báo</Text>
      {history.length === 0 ? (
        <View style={styles.emptyHistory}>
          <Text style={styles.emptyText}>Chưa có cảnh báo nào</Text>
        </View>
      ) : (
        <FlatList
          data={history}
          scrollEnabled={false}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.historyItem}>
              <Text style={styles.historyIcon}>
                {item.status === 'fire'
                  ? '🚨'
                  : item.status === 'warning'
                    ? '⚠️'
                    : item.status === 'battery'
                      ? '🪫'
                      : item.status === 'buzzer_on' || item.status === 'buzzer_off'
                        ? '🔔'
                        : '✅'}
              </Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.historyMessage}>{item.message}</Text>
                <Text style={styles.historyTime}>{item.time}</Text>
                <Text style={styles.historyMeta}>
                  Khói: {item.smoke} ppm · Pin: {item.battery}% · NL: {item.energy} Wh
                </Text>
              </View>
              <View style={[styles.historyBadge, { backgroundColor: `${getHistoryColor(item.status)}20` }]}>
                <Text style={{ color: getHistoryColor(item.status), fontSize: 11, fontWeight: '700' }}>
                  {item.status === 'fire'
                    ? 'Cháy'
                    : item.status === 'warning'
                      ? 'Khói'
                      : item.status === 'battery'
                        ? 'Pin'
                        : item.status === 'buzzer_on'
                          ? 'Bật còi'
                          : item.status === 'buzzer_off'
                            ? 'Tắt còi'
                            : 'OK'}
                </Text>
              </View>
            </View>
          )}
        />
      )}

      <View style={{ height: 36 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f1a' },
  header: { backgroundColor: '#1a1a2e', padding: 24, paddingTop: 56, alignItems: 'center' },
  headerIcon: { fontSize: 52, marginBottom: 8 },
  headerText: { color: '#fff', fontSize: 23, fontWeight: 'bold', letterSpacing: 1 },
  headerSub: { color: '#ffffff60', fontSize: 13, marginTop: 4 },
  statusCard: {
    margin: 16,
    padding: 18,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    borderWidth: 1.5,
  },
  statusIcon: { fontSize: 38 },
  statusTitle: { fontSize: 18, fontWeight: 'bold' },
  statusSub: { color: '#ffffff80', fontSize: 13, marginTop: 2 },
  updatedText: { color: '#ffffff45', fontSize: 11, marginTop: 6 },
  sectionTitle: {
    color: '#ffffff90',
    fontSize: 15,
    fontWeight: '700',
    marginHorizontal: 16,
    marginTop: 10,
    marginBottom: 10,
  },
  row: { flexDirection: 'row', paddingHorizontal: 16, gap: 12, marginBottom: 10 },
  card: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    padding: 16,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ffffff10',
    minHeight: 158,
  },
  cardDanger: { borderColor: '#ff4757', backgroundColor: '#1f1020' },
  cardIcon: { fontSize: 30, marginBottom: 6 },
  cardTitle: { color: '#ffffff80', fontSize: 13, marginBottom: 4, textAlign: 'center' },
  cardValue: { fontSize: 22, fontWeight: 'bold', marginBottom: 4, textAlign: 'center' },
  cardSubtitle: { color: '#ffffff40', fontSize: 11, marginBottom: 6, textAlign: 'center' },
  cardBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20, marginTop: 4 },
  actionRow: { flexDirection: 'row', paddingHorizontal: 16, gap: 12, marginTop: 2 },
  smallButton: { flex: 1, padding: 16, borderRadius: 18, alignItems: 'center' },
  buttonOn: { backgroundColor: '#ff4757' },
  buttonOff: { backgroundColor: '#2f3542' },
  buttonTest: { backgroundColor: '#ffa502' },
  buttonText: { color: 'white', fontSize: 15, fontWeight: 'bold' },
  resetButton: {
    marginHorizontal: 16,
    marginTop: 10,
    padding: 16,
    borderRadius: 18,
    alignItems: 'center',
    backgroundColor: '#2ed57320',
    borderWidth: 1,
    borderColor: '#2ed573',
  },
  resetButtonText: { color: '#2ed573', fontSize: 15, fontWeight: 'bold' },
  chartBox: {
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 20,
    backgroundColor: '#1a1a2e',
    borderWidth: 1,
    borderColor: '#ffffff10',
  },
  chartHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 14 },
  chartTitle: { color: '#fff', fontSize: 15, fontWeight: '700' },
  chartUnit: { color: '#ffffff50', fontSize: 12 },
  chartBars: { height: 120, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between' },
  barItem: { alignItems: 'center', flex: 1 },
  bar: { width: 20, borderRadius: 10, backgroundColor: '#ff4757' },
  barLabel: { color: '#ffffff45', fontSize: 11, marginTop: 8 },
  infoBox: {
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 20,
    backgroundColor: '#1a1a2e',
    borderWidth: 1,
    borderColor: '#ffffff10',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 11,
    borderBottomWidth: 1,
    borderBottomColor: '#ffffff10',
  },
  infoLabel: { color: '#ffffff60', fontSize: 13 },
  infoValue: { color: '#fff', fontSize: 13, fontWeight: '700' },
  settingBox: {
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 20,
    backgroundColor: '#1a1a2e',
    borderWidth: 1,
    borderColor: '#ffffff10',
  },
  inputGroup: { marginBottom: 14 },
  inputLabel: { color: '#fff', fontSize: 13, fontWeight: '700', marginBottom: 6 },
  input: {
    color: '#fff',
    borderWidth: 1,
    borderColor: '#ffffff15',
    backgroundColor: '#0f0f1a',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 14,
  },
  inputNote: { color: '#ffffff45', fontSize: 11, marginTop: 4, maxWidth: 230 },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#ffffff10',
  },
  emptyHistory: {
    marginHorizontal: 16,
    padding: 20,
    borderRadius: 20,
    backgroundColor: '#1a1a2e',
    alignItems: 'center',
  },
  emptyText: { color: '#ffffff40', fontSize: 14 },
  historyItem: {
    marginHorizontal: 16,
    marginBottom: 10,
    padding: 14,
    backgroundColor: '#1a1a2e',
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderWidth: 1,
    borderColor: '#ffffff10',
  },
  historyIcon: { fontSize: 24 },
  historyMessage: { color: '#fff', fontSize: 14, fontWeight: '600' },
  historyTime: { color: '#ffffff50', fontSize: 12, marginTop: 2 },
  historyMeta: { color: '#ffffff35', fontSize: 11, marginTop: 3 },
  historyBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
});
