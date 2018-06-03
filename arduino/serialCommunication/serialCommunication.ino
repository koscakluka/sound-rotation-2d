#define MIC_L A0 // left microphone
#define MIC_R A1 // right microphone

#define BATCH_SIZE 400

#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))

byte left_sensor_value[BATCH_SIZE];
byte right_sensor_value[BATCH_SIZE];

void setup() {
  //sbi(ADCSRA, ADPS2); sbi(ADCSRA, ADPS1); cbi(ADCSRA, ADPS0); // 9kHz sampling
  //sbi(ADCSRA, ADPS2); cbi(ADCSRA, ADPS1); sbi(ADCSRA, ADPS0); // 17kHz sampling
  sbi(ADCSRA, ADPS2); cbi(ADCSRA, ADPS1); cbi(ADCSRA, ADPS0); // 32kHz sampling
  
  Serial.begin(230400);
}

void loop() {
  long t0, t1, t2;

  t0 = micros();
  // Sample batch
  for(int i = 0; i < BATCH_SIZE; i++){
    left_sensor_value[i] = (byte)(1024 - analogRead(MIC_L));
    right_sensor_value[i] = (byte)(1024 - analogRead(MIC_R));
  }
  t1 = micros() - t0;
  
  // Start sending batch samples

  Serial.write('S'); // Send start signal
  Serial.write(BATCH_SIZE >> 8); Serial.write(BATCH_SIZE); // Send batch size (int16)
  
  for(int i = 0; i < BATCH_SIZE; i++){
    Serial.write(left_sensor_value[i]);
    Serial.write(right_sensor_value[i]);
  }

  Serial.write('E'); // Send end signal
  
  t2 = micros() - t0;


  Serial.print("Time per BATCH_SIZE samples (without transmission): ");
  Serial.print((float)t1/1000000);
  Serial.println();
  
  Serial.print("Sampling frequency:");
  Serial.print((float)BATCH_SIZE*1000000/t1);
  Serial.println();

  Serial.print("Time per BATCH_SIZE samples (with transmission): ");
  Serial.print((float)t2/1000000);
  Serial.println();

  Serial.print("Sampling frequency (with transmission):");
  Serial.print((float)BATCH_SIZE*1000000/t2);
  Serial.println();
  
  delay(2000);
}
