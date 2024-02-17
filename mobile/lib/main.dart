import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';

class MqttPage extends StatefulWidget {
  @override
  _MqttPageState createState() => _MqttPageState();
}

class _MqttPageState extends State<MqttPage> {
  final TextEditingController _publishController = TextEditingController();
  final client = MqttServerClient('broker.hivemq.com', 'flutter_client');

  bool ledState = false;
  bool relayState = false;
  bool motionDetected = false;
  int ldrValue = 0;

  double temperature = 0.0;
  String rawTemperatureData = '';

  @override
  void initState() {
    super.initState();
    client.port = 1883;
    client.keepAlivePeriod = 60;
    client.onConnected = onConnected;
    client.onDisconnected = onDisconnected;
    client.logging(on: true);
    connect();
  }

  void onConnected() {
    print('Connected to MQTT Broker');

    client.subscribe('dht22', MqttQos.atMostOnce);

    client.subscribe('motion', MqttQos.atMostOnce);

    client.subscribe('LDR', MqttQos.atMostOnce);


    client.updates?.listen((List<MqttReceivedMessage<MqttMessage>> c) {
      final MqttPublishMessage message = c[0].payload as MqttPublishMessage;
      final String payload =
      MqttPublishPayload.bytesToStringAsString(message.payload.message);


      if (c[0].topic == 'dht22') {
        setState(() {
          rawTemperatureData = payload;
          temperature = double.tryParse(payload) ?? 0.0;
        });
      } else if (c[0].topic == 'motion') {
        setState(() {
          motionDetected = payload == 'Motion detected!';
        });
      } else if (c[0].topic == 'LDR') {
        setState(() {
          ldrValue = int.tryParse(payload) ?? 0;
        });
      }
    });
  }

  void onDisconnected() {
    print('Disconnected from MQTT Broker');
  }

  Future<void> connect() async {
    try {
      await client.connect();
    } catch (e) {
      print('Exception: $e');
    }
  }

  void publishMessage(String topic, String message) {
    final builder = MqttClientPayloadBuilder();
    builder.addString(message);
    client.publishMessage(topic, MqttQos.exactlyOnce, builder.payload!);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('MQTT Communication'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        ledState = !ledState;
                        publishMessage(
                            'control', ledState ? 'led_on' : 'led_off');
                      });
                    },
                    child: Column(
                      children: [
                        Icon(
                          Icons.lightbulb,
                          size: 50,
                          color: ledState ? Colors.yellow : Colors.grey,
                        ),
                        Text('LED'),
                      ],
                    ),
                  ),
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        relayState = !relayState;
                        publishMessage('control/relay',
                            relayState ? 'open' : 'close');
                      });
                    },
                    child: Column(
                      children: [
                        Icon(
                          Icons.power,
                          size: 50,
                          color: relayState ? Colors.green : Colors.grey,
                        ),
                        Text('Relay'),
                      ],
                    ),
                  ),
                ],
              ),
              SizedBox(height: 20),
              Text('Raw Temperature Data: $rawTemperatureData'), // Display raw data
              SizedBox(height: 20),
              SfRadialGauge(
                axes: <RadialAxis>[
                  RadialAxis(
                    minimum: 0,
                    maximum: 100,
                    ranges: <GaugeRange>[
                      GaugeRange(startValue: 0, endValue: 40, color: Colors.blue),
                      GaugeRange(startValue: 40, endValue: 70, color: Colors.orange),
                      GaugeRange(startValue: 70, endValue: 100, color: Colors.red),
                    ],
                    pointers: <GaugePointer>[
                      NeedlePointer(value: temperature, enableAnimation: true),
                    ],
                    annotations: <GaugeAnnotation>[
                      GaugeAnnotation(
                        widget: Text('${temperature.toStringAsFixed(2)}°C',
                            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        angle: 90,
                        positionFactor: 0.5,
                      )
                    ],
                  )
                ],
              ),
              SizedBox(height: 20),
              Text(
                'Motion Detected: ${motionDetected ? 'Yes' : 'No'}',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: motionDetected ? Colors.red : Colors.green,
                ),
              ), // Display motion detection status
              SizedBox(height: 20),
              Text(
                'LDR Sensor Value: $ldrValue',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ), // Display LDR sensor value
            ],
          ),
        ),
      ),
    );
  }
}

void main() {
  runApp(MaterialApp(
    title: 'MQTT App',
    home: MqttPage(),
  ));
}
