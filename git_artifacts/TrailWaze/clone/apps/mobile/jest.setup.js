// Jest setup for React Native / Expo testing
import 'react-native/Libraries/Animated/NativeAnimatedHelper';

// Mock platform detection
jest.mock('react-native/Libraries/Utilities/Platform', () => ({
  OS: 'web',
  select: (obj) => obj.web,
}));
