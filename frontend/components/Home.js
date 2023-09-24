import React from 'react'
import { StyleSheet, View, Text } from 'react-native'

export default function Home(props) {
    
  return (
    <View>
    <Text style={styles.text}> Hello {props.user}, </Text>
    <Text style={styles.text}> Welcome to Machine Coaching </Text>
    </View>
  )
}

const styles = StyleSheet.create({
    text: {
      color: 'black',
      fontFamily: 'Menlo-Bold',
    },
  });
