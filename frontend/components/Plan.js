import React, { Component } from 'react'
import { View, Text, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
    bigBlue: {
      color: 'blue',
      fontWeight: 'bold',
      fontSize: 50,
      backgroundColor: '#FF6666',
      alignItems: "center" ,
      justifyContent: "center",
    },
    red: {
      color: 'red',
    },
  });


  class HttpExample extends Component {
    state = {
       data: ''
    }
    componentDidMount = () => {
       fetch('http://192.168.1.45:3000/', {
          method: 'GET'
       })
       .then((response) => response.json())
       .then((responseJson) => {
          console.log(responseJson);
          this.setState({
             data: responseJson
          })
       })
       .catch((error) => {
          console.error(error);
       });
    }
    render() {
       return (
          <View style={{justifyContent: "center", alignItems: "center", flex: 1}}>
             <Text style={styles.bigBlue}>
                {this.state.data}
             </Text>
          </View>
       )
    }
 }
 export default HttpExample