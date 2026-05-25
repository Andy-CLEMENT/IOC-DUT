export type SystemStatus = 'safe' | 'warning' | 'fire' | 'offline' | 'battery';

export type DeviceData = {
  id: string;
  name: string;
  location: string;
  smoke: number;
  battery: number;
  energy: number;
  buzzer: boolean;
  online: boolean;
  status: SystemStatus;
  updatedAt: string;
};

export type HistoryItem = {
  id: string;
  time: string;
  smoke: number;
  battery: number;
  energy: number;
  status: SystemStatus;
  message: string;
};

export const deviceData: DeviceData = {
  id: 'device01',
  name: 'Fire Sensor 01',
  location: 'Phòng Lab',
  smoke: 320,
  battery: 82,
  energy: 1.25,
  buzzer: false,
  online: true,
  status: 'safe',
  updatedAt: '16/04/2026 14:32',
};

export const historyData: HistoryItem[] = [
  {
    id: '1',
    time: '16/04/2026 14:30',
    smoke: 850,
    battery: 80,
    energy: 1.32,
    status: 'fire',
    message: 'Cảnh báo cháy',
  },
  {
    id: '2',
    time: '16/04/2026 11:15',
    smoke: 620,
    battery: 81,
    energy: 1.28,
    status: 'warning',
    message: 'Khói vượt ngưỡng',
  },
  {
    id: '3',
    time: '16/04/2026 09:20',
    smoke: 300,
    battery: 83,
    energy: 1.21,
    status: 'safe',
    message: 'Hệ thống an toàn',
  },
  {
    id: '4',
    time: '15/04/2026 20:10',
    smoke: 250,
    battery: 18,
    energy: 1.15,
    status: 'battery',
    message: 'Pin yếu',
  },
];

export function getSystemStatus(device: DeviceData) {
  if (!device.online) {
    return {
      label: 'OFFLINE',
      desc: 'Thiết bị đang mất kết nối',
      color: '#64748B',
      bg: '#F1F5F9',
      icon: 'cloud-offline-outline',
    };
  }

  if (device.status === 'fire' || device.smoke >= 800) {
    return {
      label: 'CHÁY',
      desc: 'Phát hiện khói vượt ngưỡng nguy hiểm',
      color: '#EF4444',
      bg: '#FEE2E2',
      icon: 'flame-outline',
    };
  }

  if (device.status === 'warning' || device.smoke >= 600) {
    return {
      label: 'CẢNH BÁO',
      desc: 'Nồng độ khói đang tăng cao',
      color: '#F97316',
      bg: '#FFEDD5',
      icon: 'warning-outline',
    };
  }

  return {
    label: 'AN TOÀN',
    desc: 'Hệ thống đang hoạt động bình thường',
    color: '#22C55E',
    bg: '#DCFCE7',
    icon: 'checkmark-circle-outline',
  };
}

export function getHistoryColor(status: SystemStatus) {
  if (status === 'fire') return '#EF4444';
  if (status === 'warning' || status === 'battery') return '#F97316';
  if (status === 'offline') return '#64748B';
  return '#22C55E';
}