import React, {useState} from 'react'
import { View, Text, StyleSheet, Pressable} from 'react-native'
import {TextInput, Button} from 'react-native-paper';

function Create(props) {
    const[year, setYear] =  useState("")
    const[month, setMonth] =  useState("")
    const[day, setDay] =  useState("")
    const[weeks, setWeeks] =  useState("")
    const[min, setMin] =  useState("")
    const[sec, setSec] =  useState("")
    const[dist, setDist] =  useState("")

    const createPlan = () => {
        fetch('http://192.168.1.45:3000/api', {
            method: 'POST',
            headers: {
                'Content-Type':'application/json'
            },
            body: JSON.stringify({year:year})
        })
        .then(response => response.json())
        .then((responseJson) => console.log(responseJson))
        .catch(error => console.log(error))
    }

  return (
    <View>
        <TextInput
        label = 'Race Year'
        value = {year}
        mode = 'outlined'
        onChangeText = {text => setYear(text)}
        />
        <TextInput
        label = 'Race Month'
        value = {month}
        mode = 'outlined'
        onChangeText = {text => setMonth(text)}
        />
        <TextInput
        label = 'Race Day'
        value = {day}
        mode = 'outlined'
        onChangeText = {text => setDay(text)}
        />
        <TextInput
        label = 'Training Weeks'
        value = {weeks}
        mode = 'outlined'
        onChangeText = {text => setWeeks(text)}
        />
        <TextInput
        label = 'Goal Pace Minutes'
        value = {min}
        mode = 'outlined'
        onChangeText = {text => setMin(text)}
        />
        <TextInput
        label = 'Goal Pace Seconds'
        value = {sec}
        mode = 'outlined'
        onChangeText = {text => setSec(text)}
        />
        <TextInput
        label = 'Distance'
        value = {dist}
        mode = 'outlined'
        onChangeText = {text => setDist(text)}
        />
        <Button
        style = {{margin: 10, width: 200}}
        textColor="white" 
        buttonColor='blue'
        mode = 'contained'
        onPress = {() => createPlan()}
        > Create Plan </Button>

    </View>
  )
}

export default Create