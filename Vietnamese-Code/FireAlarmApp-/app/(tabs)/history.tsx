import { Ionicons } from '@expo/vector-icons';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { getHistoryColor, historyData } from '../data';

export default function HistoryScreen() {
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Lịch sử cảnh báo</Text>
        <Text style={styles.subtitle}>Các sự kiện gần đây của hệ thống</Text>
      </View>

      {historyData.map((item) => {
        const color = getHistoryColor(item.status);

        return (
          <View key={item.id} style={styles.item}>
            <View style={[styles.iconBox, { backgroundColor: `${color}15` }]}>
              <Ionicons
                name={
                  item.status === 'fire'
                    ? 'flame-outline'
                    : item.status === 'warning'
                      ? 'warning-outline'
                      : item.status === 'battery'
                        ? 'battery-dead-outline'
                        : 'checkmark-circle-outline'
                }
                size={25}
                color={color}
              />
            </View>

            <View style={{ flex: 1 }}>
              <Text style={styles.message}>{item.message}</Text>
              <Text style={styles.time}>{item.time}</Text>
              <Text style={styles.meta}>
                Khói: {item.smoke} dB/m · Pin: {item.battery}% · NL: {item.energy} Wh
              </Text>
            </View>

            <Text style={[styles.status, { color }]}>{item.status}</Text>
          </View>
        );
      })}

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
  item: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 14,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 1,
  },
  iconBox: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  message: {
    color: '#111827',
    fontSize: 15,
    fontWeight: '800',
  },
  time: {
    color: '#64748B',
    fontSize: 12,
    marginTop: 3,
  },
  meta: {
    color: '#94A3B8',
    fontSize: 11,
    marginTop: 3,
  },
  status: {
    fontSize: 12,
    fontWeight: '900',
  },
});