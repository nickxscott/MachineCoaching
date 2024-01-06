import React, { Component } from 'react'
import { StyleSheet, View, Text, Button} from 'react-native'

class ClassHome extends Component {

  state = {
    user:"Nick"
  }
  render() {
    return (
      <View>
        <Text style={styles.text}> Hello {this.state.user}, </Text>
        <Text style={styles.text}> Welcome to Machine Coaching </Text>
        <Button style={styles.Button} 
                title='Start Training' 
                onPress={() => this.setState({user: 'new user'})}/>
      </View>
    )
  }
}

export default ClassHome

const styles = StyleSheet.create({
    text: {
      color: 'black',
      fontFamily: 'Menlo-Bold',
    },
    button: {
        borderColor: 'black',
        color:'blue'
    }
  });

