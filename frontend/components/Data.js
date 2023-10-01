import React,  {useState, useEffect} from 'react'
import { StyleSheet, View, Text, Button, FlatList} from 'react-native'
import { Card, FAB } from 'react-native-paper'

export default function Data() {

  const [data, setData] = useState([])

  useEffect(() => {
      fetch('http://192.168.1.45:3000/', {
        method: 'GET'
      })
      .then(resp => resp.json())
      .then(pace => {
        setData(pace)
      })
  }, [])

  const renderData = (item) => {
    return (
        <Card style = {styles.cardStyle}>
            <Text style={styles.text}>{item.title}</Text>
            <Text style={styles.text}>{item.body}</Text>
        </Card>
    )
  }
    
  return (
    <View style={{flex:1}}>
        <FlatList 
        data = {data}
        renderItem={({item}) =>{
            return renderData(item)
            }}
        keyExtractor={item => '${item.id}'}
        />

        <FAB
        style = {styles.fab}
        small = {false}
        icon='plus'
        theme={{colors:{accent:'green'}}}
        onPress = {() => console.log('Pressed')}
        />

    </View>
  )
}

const styles = StyleSheet.create({
    text: {
      color: 'black',
      fontFamily: 'Menlo-Regular'
    },
    cardStyle: {
        margin: 10,
        padding: 10

    },
    fab: {
        position: 'absolute',
        margin: 10,
        right: 0,
        bottom: 0
    }
  });