import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Dimensions} from 'react-native';
import Home from './components/Home'
import Data from './components/Data'
import Create from './components/Create'
import Plan from './components/Plan';
import ClassHome from './components/ClassHome';
import Contants from 'expo-constants'

import { NavigationContainer } from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'

const Stack = createStackNavigator()
const windowWidth = Dimensions.get('window').width;

function App() {

  const name = "Nick"
  
  return (
      <Stack.Navigator>
        <Stack.Screen name = "Home" component = {Home}/>
        <Stack.Screen name = "Create" component = {Create}/>
        <Stack.Screen name = "Plan" component = {Plan}/>
      </Stack.Navigator>      
  );
}

export default() => {
  return (
    <NavigationContainer>
      <App/>
    </NavigationContainer>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'blue',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Contants.statusBarHeight,
    padding: 10
  },
  nav: {
    backgroundColor: 'red',
    width: 1000
  }
});
