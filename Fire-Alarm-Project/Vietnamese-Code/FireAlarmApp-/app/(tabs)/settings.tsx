import { Ionicons } from '@expo/vector-icons';
import { useState } from 'react';
import {
  Alert,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

export default function SettingsScreen() {
  const [smokeWarning, setSmokeWarning] = useState('0.05');
  const [smokeFire, setSmokeFire] = useState('0.15');
  const [batteryLow, setBatteryLow] = useState('20');
  const [notificationEnabled, setNotificationEnabled] = useState(true);

  const saveSettings = () => {
    Alert.alert('Đã lưu', 'Cài đặt đã được lưu tạm trên app preview.');
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Cài đặt</Text>
        <Text style={styles.subtitle}>Cấu hình ngưỡng cảnh báo</Text>
      </View>

      <View style={styles.card}>
        <SettingInput
          label="Ngưỡng cảnh báo khói"
          value={smokeWarning}
          onChangeText={setSmokeWarning}
          unit="dB/m"
        />

        <SettingInput
          label="Ngưỡng cháy nguy hiểm"
          value={smokeFire}
          onChangeText={setSmokeFire}
          unit="dB/m"
        />

        <SettingInput
          label="Ngưỡng pin yếu"
          value={batteryLow}
          onChangeText={setBatteryLow}
          unit="%"
        />

        <View style={styles.switchRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.label}>Thông báo cảnh báo</Text>
            <Text style={styles.note}>Bật thông báo khi có khói/cháy</Text>
          </View>

          <Switch
            value={notificationEnabled}
            onValueChange={setNotificationEnabled}
          />
        </View>
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={saveSettings}>
        <Ionicons name="save-outline" size={22} color="#FFFFFF" />
        <Text style={styles.saveButtonText}>Lưu cài đặt</Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

type SettingInputProps = {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  unit: string;
};

function SettingInput({
  label,
  value,
  onChangeText,
  unit,
}: SettingInputProps) {
  return (
    <View style={styles.inputBlock}>
      <Text style={styles.label}>{label}</Text>

      <View style={styles.inputRow}>
        <TextInput
          value={value}
          onChangeText={onChangeText}
          keyboardType="numeric"
          style={styles.input}
          placeholder="Nhập giá trị"
          placeholderTextColor="#94A3B8"
        />

        <Text style={styles.unit}>{unit}</Text>
      </View>
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
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  inputBlock: {
    marginBottom: 16,
  },
  label: {
    color: '#111827',
    fontSize: 14,
    fontWeight: '800',
    marginBottom: 8,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: 12,
  },
  input: {
    flex: 1,
    height: 48,
    color: '#111827',
    fontSize: 16,
  },
  unit: {
    color: '#64748B',
    fontWeight: '800',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  note: {
    color: '#64748B',
    fontSize: 12,
  },
  saveButton: {
    marginTop: 16,
    backgroundColor: '#EF4444',
    padding: 16,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 8,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontWeight: '900',
    fontSize: 16,
  },
});