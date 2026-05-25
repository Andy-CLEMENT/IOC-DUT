import { Link } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { deviceData, getSystemStatus } from '../../data';

export default function DeviceListScreen() {
  const status = getSystemStatus(deviceData);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Thiết bị</Text>
        <Text style={styles.subtitle}>Danh sách thiết bị báo cháy</Text>
      </View>

      <Link href={'/devices/device01' as any} asChild>
        <TouchableOpacity style={styles.card}>
          <View style={styles.iconBox}>
            <Ionicons name="server-outline" size={34} color="#EF4444" />
          </View>

          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{deviceData.name}</Text>
            <Text style={styles.location}>{deviceData.location}</Text>
            <Text style={[styles.status, { color: status.color }]}>
              {status.label}
            </Text>
          </View>

          <Ionicons name="chevron-forward-outline" size={26} color="#94A3B8" />
        </TouchableOpacity>
      </Link>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 16,
  },
  header: {
    paddingTop: 58,
    paddingBottom: 20,
  },
  title: {
    color: '#111827',
    fontSize: 28,
    fontWeight: '900',
  },
  subtitle: {
    color: '#64748B',
    marginTop: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  iconBox: {
    width: 58,
    height: 58,
    borderRadius: 20,
    backgroundColor: '#FEE2E2',
    alignItems: 'center',
    justifyContent: 'center',
  },
  name: {
    color: '#111827',
    fontSize: 18,
    fontWeight: '900',
  },
  location: {
    color: '#64748B',
    marginTop: 3,
  },
  status: {
    marginTop: 6,
    fontSize: 12,
    fontWeight: '900',
  },
});