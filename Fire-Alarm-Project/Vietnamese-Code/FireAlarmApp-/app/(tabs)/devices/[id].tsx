import { Link, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { deviceData, getSystemStatus } from '../../data';

export default function DeviceDetailScreen() {
  const { id } = useLocalSearchParams();
  const status = getSystemStatus(deviceData);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Link href={'/devices' as any} asChild>
          <TouchableOpacity style={styles.backButton}>
            <Ionicons name="arrow-back-outline" size={22} color="#111827" />
            <Text style={styles.backText}>Quay lại</Text>
          </TouchableOpacity>
        </Link>

        <View style={styles.bigIconBox}>
          <Ionicons name="server-outline" size={52} color="#EF4444" />
        </View>

        <Text style={styles.title}>{deviceData.name}</Text>
        <Text style={styles.subtitle}>Mã thiết bị: {id}</Text>
      </View>

      <View style={[styles.statusCard, { backgroundColor: status.bg }]}>
        <Ionicons name={status.icon as any} size={40} color={status.color} />

        <View style={{ flex: 1 }}>
          <Text style={[styles.statusTitle, { color: status.color }]}>
            {status.label}
          </Text>
          <Text style={styles.statusDesc}>{status.desc}</Text>
        </View>
      </View>

      <View style={styles.infoBox}>
        <InfoRow label="Tên thiết bị" value={deviceData.name} />
        <InfoRow label="Mã thiết bị" value={deviceData.id} />
        <InfoRow label="Vị trí" value={deviceData.location} />
        <InfoRow label="Kết nối" value={deviceData.online ? 'Online' : 'Offline'} />
        <InfoRow label="Nồng độ khói" value={`${deviceData.smoke} dB/m`} />
        <InfoRow label="Pin" value={`${deviceData.battery}%`} />
        <InfoRow label="Năng lượng" value={`${deviceData.energy} Wh`} />
        <InfoRow label="Còi báo động" value={deviceData.buzzer ? 'Đang bật' : 'Đang tắt'} />
        <InfoRow label="Cập nhật lần cuối" value={deviceData.updatedAt} />
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 16,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    alignItems: 'center',
  },
  backButton: {
    alignSelf: 'flex-start',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 8,
  },
  backText: {
    color: '#111827',
    fontSize: 16,
    fontWeight: '800',
  },
  bigIconBox: {
    width: 96,
    height: 96,
    borderRadius: 32,
    backgroundColor: '#FEE2E2',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
  },
  title: {
    color: '#111827',
    fontSize: 26,
    fontWeight: '900',
    marginTop: 14,
  },
  subtitle: {
    color: '#64748B',
    marginTop: 4,
  },
  statusCard: {
    padding: 18,
    borderRadius: 24,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 16,
  },
  statusTitle: {
    fontSize: 22,
    fontWeight: '900',
  },
  statusDesc: {
    color: '#374151',
    marginTop: 4,
  },
  infoBox: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 13,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  label: {
    color: '#64748B',
    flex: 1,
  },
  value: {
    color: '#111827',
    fontWeight: '900',
    flex: 1,
    textAlign: 'right',
  },
});