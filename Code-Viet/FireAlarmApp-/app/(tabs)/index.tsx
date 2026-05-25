import { Ionicons } from '@expo/vector-icons';
import { Link } from 'expo-router';
import { onValue, ref } from 'firebase/database';
import { useEffect, useState } from 'react';
import {
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { database } from '../../firebaseConfig';
import {
  getSystemStatus,
  deviceData as mockDeviceData,
  historyData as mockHistoryData,
} from '../data';

const screenWidth = Dimensions.get('window').width;

export default function DashboardScreen() {
  const [deviceData, setDeviceData] = useState(mockDeviceData);
  const [historyData, setHistoryData] = useState(mockHistoryData);

  useEffect(() => {
    const deviceRef = ref(database, 'devices/fire_alarm_01');

    const unsubscribeDevice = onValue(
      deviceRef,
      (snapshot) => {
        const data = snapshot.val();

        console.log('Firebase device data:', data);

        if (data) {
          const buzzerFromFirebase =
            data.buzzer !== undefined
              ? Boolean(data.buzzer)
              : Boolean(data.fireWarning || data.emergency || mockDeviceData.buzzer);

          setDeviceData({
            ...mockDeviceData,
            smoke: Number(data.smoke ?? mockDeviceData.smoke),
            battery: Number(data.battery ?? mockDeviceData.battery),
            energy: Number(data.energy ?? mockDeviceData.energy),
            buzzer: buzzerFromFirebase,
            updatedAt: String(
              data.updatedAt ??
                data.timestamp ??
                mockDeviceData.updatedAt
            ),
          });
        }
      },
      (error) => {
        console.log('Lỗi đọc devices/fire_alarm_01:', error.message);
      }
    );

    const historyRef = ref(database, 'history/fire_alarm_01');

    const unsubscribeHistory = onValue(
      historyRef,
      (snapshot) => {
        const data = snapshot.val();

        console.log('Firebase history data:', data);

        if (data) {
          const list = Object.keys(data)
            .map((key) => {
              const item = data[key];

              const buzzerFromFirebase =
                item.buzzer !== undefined
                  ? Boolean(item.buzzer)
                  : Boolean(item.fireWarning || item.emergency);

              return {
                ...mockHistoryData[0],
                smoke: Number(item.smoke ?? 0),
                battery: Number(item.battery ?? 0),
                energy: Number(item.energy ?? 0),
                buzzer: buzzerFromFirebase,
                updatedAt: String(item.updatedAt ?? item.timestamp ?? item.time ?? ''),
              };
            })
            .reverse();

          setHistoryData(list);
        }
      },
      (error) => {
        console.log('Lỗi đọc history/fire_alarm_01:', error.message);
      }
    );

    return () => {
      unsubscribeDevice();
      unsubscribeHistory();
    };
  }, []);

  const system = getSystemStatus(deviceData);
  const smokeValues = historyData.slice(0, 6).reverse();

  const smokeChartData =
    smokeValues.length > 0
      ? smokeValues.map((item) => item.smoke)
      : [0, 0, 0, 0, 0, 0];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Fire Alarm System</Text>
          <Text style={styles.subtitle}>Giám sát báo cháy realtime</Text>
        </View>

        <View style={styles.headerIcon}>
          {/* <Ionicons name="flame-outline" size={28} color="#EF4444" /> */}
          {/* <Ionicons name="notifications-outline" size={28} color="#ffec44" /> */}
          <Ionicons name="notifications" size={28} color="#f5f103" />
        </View>
      </View>

      <View style={[styles.statusCard, { backgroundColor: system.bg }]}>
        <Ionicons name={system.icon as any} size={42} color={system.color} />

        <View style={{ flex: 1 }}>
          <Text style={[styles.statusTitle, { color: system.color }]}>
            {system.label}
          </Text>
          <Text style={styles.statusDesc}>{system.desc}</Text>
          <Text style={styles.updateText}>Cập nhật: {deviceData.updatedAt}</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Thông số hiện tại</Text>

      <View style={styles.grid}>
        <MetricCard
          title="Khói"
          value={`${deviceData.smoke} dB/m`}
          icon="cloud-outline"
          color="#EF4444"
        />

        <MetricCard
          title="Pin"
          value={`${deviceData.battery}%`}
          icon="battery-half-outline"
          color="#000000"
        />

        <MetricCard
          title="Năng lượng"
          value={`${deviceData.energy} Wh`}
          icon="flash-outline"
          color="#F59E0B"
        />

        <MetricCard
          title="Còi"
          value={deviceData.buzzer ? 'Bật' : 'Tắt'}
          icon={deviceData.buzzer ? 'volume-high-outline' : 'volume-mute-outline'}
          color={deviceData.buzzer ? '#EF4444' : '#22C55E'}
        />
      </View>

      <Text style={styles.sectionTitle}>Biểu đồ khói</Text>

      <View style={styles.chartBox}>
        <LineChart
          data={{
            labels: smokeChartData.map((_, index) => `${index + 1}`),
            datasets: [
              {
                data: smokeChartData,
              },
            ],
          }}
          width={screenWidth - 32}
          height={220}
          yAxisSuffix=""
          chartConfig={{
            backgroundGradientFrom: '#FFFFFF',
            backgroundGradientTo: '#FFFFFF',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(239, 68, 68, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(100, 116, 139, ${opacity})`,
            propsForDots: {
              r: '5',
              strokeWidth: '2',
              stroke: '#EF4444',
            },
            propsForBackgroundLines: {
              stroke: '#E5E7EB',
            },
          }}
          bezier
          style={styles.lineChart}
        />
      </View>

      <View style={styles.linkRow}>
        <Link href={'/devices/device01' as any} asChild>
          <TouchableOpacity style={styles.linkButton}>
            <Text style={styles.linkButtonText}>Xem chi tiết thiết bị</Text>
          </TouchableOpacity>
        </Link>

        <Link href={'/history' as any} asChild>
          <TouchableOpacity style={styles.secondaryButton}>
            <Text style={styles.secondaryButtonText}>Xem lịch sử</Text>
          </TouchableOpacity>
        </Link>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function MetricCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string;
  icon: any;
  color: string;
}) {
  return (
    <View style={styles.metricCard}>
      <View style={[styles.metricIconBox, { backgroundColor: `${color}15` }]}>
        <Ionicons name={icon} size={26} color={color} />
      </View>

      <Text style={styles.metricTitle}>{title}</Text>
      <Text style={[styles.metricValue, { color }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    paddingTop: 58,
    paddingHorizontal: 20,
    paddingBottom: 22,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    color: '#111827',
    fontSize: 26,
    fontWeight: '900',
  },
  subtitle: {
    color: '#64748B',
    marginTop: 4,
  },
  headerIcon: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusCard: {
    margin: 16,
    padding: 18,
    borderRadius: 24,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  statusTitle: {
    fontSize: 24,
    fontWeight: '900',
  },
  statusDesc: {
    color: '#374151',
    marginTop: 4,
  },
  updateText: {
    color: '#64748B',
    marginTop: 8,
    fontSize: 12,
  },
  sectionTitle: {
    color: '#111827',
    fontSize: 18,
    fontWeight: '900',
    marginHorizontal: 16,
    marginTop: 8,
    marginBottom: 12,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    paddingHorizontal: 16,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  metricIconBox: {
    width: 44,
    height: 44,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  metricTitle: {
    color: '#64748B',
    fontSize: 13,
  },
  metricValue: {
    fontSize: 21,
    fontWeight: '900',
    marginTop: 4,
  },
  chartBox: {
    marginHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
    overflow: 'hidden',
  },
  lineChart: {
    borderRadius: 20,
  },
  linkRow: {
    padding: 16,
    gap: 10,
  },
  linkButton: {
    backgroundColor: '#EF4444',
    padding: 16,
    borderRadius: 18,
    alignItems: 'center',
  },
  linkButtonText: {
    color: '#FFFFFF',
    fontWeight: '900',
  },
  secondaryButton: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 18,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  secondaryButtonText: {
    color: '#111827',
    fontWeight: '900',
  },
});