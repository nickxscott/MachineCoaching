
import React,  {useState, useEffect} from 'react'
import { StyleSheet, View, Text, Button, FlatList, Dimensions} from 'react-native'
import { Card, FAB } from 'react-native-paper'
import Contants from 'expo-constants'

export default function Home(props) {

  return (
    <View style={styles.container}>
      <Text style={styles.text}> Hello, </Text>
      <Text style={styles.text}> Welcome to Machine Coaching </Text>
      <FAB
      style = {styles.fab}
      label = 'Start Training'
      icon='plus'
      onPress = {() => props.navigation.navigate('Create')}
      />  
    </View>
  )
}

const styles = StyleSheet.create({
    text: {
      color: 'black',
      fontFamily: 'Menlo-Bold',
    },
    cardStyle: {
      margin: 10,
      padding: 10

    },
    fab: {
      padding: 3,
      margin: 15
  },
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
    /*marginTop: Contants.statusBarHeight, REMOVED AFTER ADDING NAVIGATION*/
    padding: 20,
  }
  });
  
 