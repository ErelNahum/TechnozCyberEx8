package com.kirelcodes.log4j;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.util.Scanner;

public class Client {
	private String username;
	private String password;
	private String host;
	private int port;
	private Socket clientSocket;
	private OutputStream out;
	private InputStream  in;
	JSONParser parser;
	static final Logger logger = LogManager.getLogger(Client.class.getName());

	public Client(String config) throws FileNotFoundException, ParseException
	{
		File configFile = new File(config);
		Scanner s = new Scanner(configFile);
		String configJson = s.nextLine();
		parser = new JSONParser();
		JSONObject obj = (JSONObject) parser.parse(configJson);
		this.username = (String) obj.get("user");
		this.password = (String) obj.get("password");
		this.host = (String) obj.get("server");
		this.port = Integer.parseInt((String) obj.get("port"));
	}

	public void connect() throws IOException
	{
		if(clientSocket != null || out != null || in != null)
			throw new RuntimeException("Connection already in progress");
		clientSocket = new Socket(this.host, port);
		out = clientSocket.getOutputStream();
		in = clientSocket.getInputStream();
	}

	/**
	 * This function receives a packet, adds the username and password into it and returns the response
	 * @param packet raw_packet, without username and password
	 * @return response packet
	 */
	public JSONObject sendPacket(JSONObject packet) throws IOException, ParseException {
		if(clientSocket == null || out == null || in == null)
			throw new RuntimeException("Connection not opened yet");
		packet.put("user", username);
		packet.put("pass", password);
		String payload = packet.toJSONString();
		int length = payload.length();

		ByteBuffer dbuf = ByteBuffer.allocate(4);
		dbuf.order(ByteOrder.LITTLE_ENDIAN);
		dbuf.putInt(length);
		byte[] lengthBuff = dbuf.array();

		out.write(lengthBuff);
		out.write(payload.getBytes());
		out.flush();


		if(in.read(lengthBuff) != 4) {
			throw new RuntimeException("Incorrect length received");
		}
		dbuf = ByteBuffer.wrap(lengthBuff);
		dbuf.order(ByteOrder.LITTLE_ENDIAN);
		length = dbuf.getInt();

		byte[] buffer = new byte[length];
		int readRes = in.read(buffer);
		if(length != readRes)
			throw new RuntimeException("Incorrect amount of chars received " + readRes + " vs " + length);

		return (JSONObject) parser.parse(new String(buffer));
	}

	public void disconnect() throws IOException
	{
		in.close();
		in  = null;
		out.close();
		out = null;
		clientSocket.close();
		clientSocket = null;
	}

	public static void main(String[] args)
	{
		try
		{
			Client c = new Client("settings.dat");
			JSONObject get_mail = new JSONObject();
			get_mail.put("ID", 2);
			c.connect();

			JSONObject response = c.sendPacket(get_mail);
			c.disconnect();
			JSONArray array = (JSONArray)response.get("mails");
			for(int i = 0; i < array.size(); ++i)
			{
				JSONObject mail = (JSONObject) array.get(i);
				String from = (String) mail.get("from");
				String subject = (String) mail.get("subject");
				String data = (String) mail.get("data");

				logger.error("Received a new message from " + from + " with title " + subject);

				from = from.split("\\\\")[0];
				subject = subject.split("\\\\")[0];
				from = from.split("/")[0];
				subject = subject.split("/")[0];//No path traversal on me

				File fromF = new File(from);//mmm might be a security threat as well
				if(!fromF.exists())
					fromF.mkdir();
				File path = new File(from, subject);
				FileWriter subjectF = new FileWriter(path.getPath());
				subjectF.write(data);
				subjectF.close();
			}
		}
		catch (FileNotFoundException e)
		{
			e.printStackTrace();
			System.err.println("settings.dat file not found");
		}
		catch (ParseException e)
		{
			System.err.println("Invalid json");
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
