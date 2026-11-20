<template>
  <div class="w-14 h-14 rounded-xl bg-white border border-slate-900/15 flex items-center justify-center overflow-hidden relative shadow-xs select-none pointer-events-none">
    <!-- 1. Arduino Uno -->
    <div v-if="itemId === 'ARDUINO_UNO'" class="scale-[0.22] origin-center flex items-center justify-center">
      <wokwi-arduino-uno></wokwi-arduino-uno>
    </div>

    <!-- 2. Arduino Nano -->
    <div v-else-if="itemId === 'ARDUINO_NANO'" class="scale-[0.34] origin-center flex items-center justify-center">
      <wokwi-arduino-nano></wokwi-arduino-nano>
    </div>

    <!-- 3. Arduino Mega -->
    <div v-else-if="itemId === 'ARDUINO_MEGA'" class="scale-[0.16] origin-center flex items-center justify-center">
      <wokwi-arduino-mega></wokwi-arduino-mega>
    </div>

    <!-- 4. ESP32 -->
    <div v-else-if="itemId === 'ESP32'" class="scale-[0.25] origin-center flex items-center justify-center">
      <wokwi-esp32-devkit-v1></wokwi-esp32-devkit-v1>
    </div>

    <!-- 5. Breadboard -->
    <div v-else-if="itemId.startsWith('BREADBOARD')" class="scale-[0.17] origin-center flex items-center justify-center">
      <wokwi-breadboard-half></wokwi-breadboard-half>
    </div>

    <!-- 6. LEDs -->
    <div v-else-if="itemId === 'LED_RED'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-led color="red" value="1"></wokwi-led>
    </div>
    <div v-else-if="itemId === 'LED_GREEN'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-led color="green" value="1"></wokwi-led>
    </div>
    <div v-else-if="itemId === 'LED_BLUE'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-led color="blue" value="1"></wokwi-led>
    </div>
    <div v-else-if="itemId === 'LED_YELLOW'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-led color="yellow" value="1"></wokwi-led>
    </div>
    <div v-else-if="itemId === 'LED_RGB' || itemId === 'NEOPIXEL_STRIP'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-rgb-led></wokwi-rgb-led>
    </div>

    <!-- 7. Dirençler -->
    <div v-else-if="itemId === 'RESISTOR_220'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-resistor value="220"></wokwi-resistor>
    </div>
    <div v-else-if="itemId === 'RESISTOR_1K'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-resistor value="1000"></wokwi-resistor>
    </div>
    <div v-else-if="itemId === 'RESISTOR_10K'" class="scale-[0.7] origin-center flex items-center justify-center">
      <wokwi-resistor value="10000"></wokwi-resistor>
    </div>

    <!-- 8. Potansiyometre & Buton & Switch -->
    <div v-else-if="itemId === 'POTENTIOMETER'" class="scale-[0.55] origin-center flex items-center justify-center">
      <wokwi-potentiometer></wokwi-potentiometer>
    </div>
    <div v-else-if="itemId === 'PUSH_BUTTON'" class="scale-[0.6] origin-center flex items-center justify-center">
      <wokwi-pushbutton color="red"></wokwi-pushbutton>
    </div>
    <div v-else-if="itemId === 'SLIDE_SWITCH'" class="scale-[0.65] origin-center flex items-center justify-center">
      <wokwi-slide-switch></wokwi-slide-switch>
    </div>

    <!-- 9. Sensörler -->
    <div v-else-if="itemId === 'LDR_DISCRETE' || itemId === 'LDR_SENSOR'" class="scale-[0.9] origin-center flex items-center justify-center">
      <wokwi-photoresistor></wokwi-photoresistor>
    </div>
    <div v-else-if="itemId === 'LDR_MODULE' || itemId === 'LDR_4PIN'" class="scale-[0.32] origin-center flex items-center justify-center">
      <wokwi-photoresistor-sensor></wokwi-photoresistor-sensor>
    </div>
    <div v-else-if="itemId === 'HCSR04'" class="scale-[0.35] origin-center flex items-center justify-center">
      <wokwi-hc-sr04></wokwi-hc-sr04>
    </div>
    <div v-else-if="itemId === 'PIR_SENSOR'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-pir-motion-sensor></wokwi-pir-motion-sensor>
    </div>
    <div v-else-if="itemId === 'DHT11' || itemId === 'DHT22'" class="scale-[0.5] origin-center flex items-center justify-center">
      <wokwi-dht22></wokwi-dht22>
    </div>
    <div v-else-if="itemId === 'JOYSTICK_MODULE'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-analog-joystick></wokwi-analog-joystick>
    </div>

    <!-- 10. Aktüatörler & Ses -->
    <div v-else-if="itemId === 'BUZZER' || itemId === 'ACTIVE_BUZZER'" class="scale-[0.5] origin-center flex items-center justify-center">
      <wokwi-buzzer></wokwi-buzzer>
    </div>
    <div v-else-if="itemId === 'SERVO_SG90'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-servo></wokwi-servo>
    </div>
    <div v-else-if="itemId === 'LCD_16X2_I2C'" class="scale-[0.23] origin-center flex items-center justify-center">
      <wokwi-lcd1602></wokwi-lcd1602>
    </div>
    <div v-else-if="itemId === 'SEVEN_SEGMENT'" class="scale-[0.5] origin-center flex items-center justify-center">
      <wokwi-7segment></wokwi-7segment>
    </div>
    <div v-else-if="itemId === 'OLED_096_I2C'" class="scale-[0.5] origin-center flex items-center justify-center">
      <wokwi-ssd1306></wokwi-ssd1306>
    </div>

    <!-- 11. Bluetooth & Motor Sürücüler & Röle -->
    <div v-else-if="itemId === 'BLUETOOTH_HC05' || itemId === 'BLUETOOTH_HC06'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-hc-05></wokwi-hc-05>
    </div>
    <div v-else-if="itemId === 'MOTOR_DRIVER_L293D'" class="scale-[0.38] origin-center flex items-center justify-center">
      <wokwi-l293d></wokwi-l293d>
    </div>
    <div v-else-if="itemId === 'MOTOR_DRIVER_L298N'" class="scale-[0.38] origin-center flex items-center justify-center">
      <wokwi-l298n></wokwi-l298n>
    </div>
    <div v-else-if="itemId === 'DC_MOTOR_5V'" class="scale-[0.45] origin-center flex items-center justify-center">
      <wokwi-dc-motor></wokwi-dc-motor>
    </div>
    <div v-else-if="itemId === 'RELAY_MODULE'" class="scale-[0.42] origin-center flex items-center justify-center">
      <wokwi-relay-module></wokwi-relay-module>
    </div>
    <div v-else-if="itemId === 'SOIL_MOISTURE'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-soil-moisture-sensor></wokwi-soil-moisture-sensor>
    </div>
    <div v-else-if="itemId === 'RAIN_SENSOR'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-rain-sensor></wokwi-rain-sensor>
    </div>
    <div v-else-if="itemId === 'WATER_SENSOR'" class="scale-[0.4] origin-center flex items-center justify-center">
      <wokwi-water-sensor></wokwi-water-sensor>
    </div>

    <!-- Diğer Parçalar veya Özel Eklenenler İçin İkon -->
    <span v-else class="text-2xl">{{ icon || '🧪' }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  itemId: string;
  icon?: string;
}>();
</script>
