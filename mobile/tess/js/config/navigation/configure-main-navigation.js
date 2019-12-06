/**
 * SLAC 2017
 *
 * Created by: jongon
 *
 * Setup the whole application navigation. 
 */

import React from 'react'
import { connect } from 'react-redux'
import { Image, Text } from 'react-native'
import { createAppContainer, createBottomTabNavigator, createSwitchNavigator, createStackNavigator } from 'react-navigation'



const RootNavigatorWrapper = createAppContainer(switchNavigator);
export default RootNavigatorWrapper
