import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import Home from './components/Home'
import Data from './components/Data'
import ClassHome from './components/ClassHome';
import Contants from 'expo-constants'

export default function App() {

  const name = "Nick"

  return (
    <View style={styles.container}>
      <Home user = {name}/>
       {/* <Data/> */}
      
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Contants.statusBarHeight,
    padding: 20
  },
});
