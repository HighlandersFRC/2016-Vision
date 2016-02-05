/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package networking;

import static com.oracle.jrockit.jfr.DataType.INTEGER;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Scanner;

/**
 *
 * @author void
 */
public class JavaSocketServer {

   // Values will be read in the form (xValue,yValue)
    public static void main(String[] args) throws IOException {
        int port = 5801;
        String fromClient = "";
        String toClient = "";
        boolean run = true;
        ServerSocket serverSocket = new ServerSocket(port);
        while (run) {
            fromClient = "";
            Socket socket = serverSocket.accept();
            System.out.println("Got Connection from: " + socket.getLocalAddress());
            while (run && fromClient != null) {
               BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                //PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                fromClient = in.readLine();
                
               // int point[] = parsePoint(fromClient);
               // Scanner scanner = new Scanner(fromClient);
                //int x = scanner.nextInt();
                // int y = scanner.nextInt();
                
                 System.out.println("received: " + fromClient); 
            }

        }

    }

    public static int[] parsePoint(String line) {
        int point[] = {0,0};
        int position = 0;
        while(line.charAt(position) != '('){
            position++;
        }
        position++;
        while (line.charAt(position) != ',') {
            point[0] = (point[0] * 10) + (int)line.charAt(position) - 48;
            System.out.println(point[0]);
            position++;
        }
        position++;
        while (line.charAt(position) != ')') {
            point[1] = (point[1] * 10) + (int)line.charAt(position) - 48;
            position++;
        }

        return point;

    }
}
