function TTaskMap

    [map,x,y] = readDTMv1('DTM05_v1.txt');
%     [map,x,y] = readDTMv1('DTM01_v1.txt');
%     [map,x,y] = readDTMv2('DTM05_v2.txt');
%     [map,x,y] = readDTMv2('DTM01_v2.txt');

    figure('Position',[50 100 1000 530]);
    axes('Position',[0.06,0.1,0.90,0.83]);
    pcolor(x, y, map);
    cmap = 1 + 0.5 *(jet(27)-1);
    cmap(end,:) = [0 0 0];
    colormap(cmap);
    axis equal;
    hold on;
    set(gca,'XTick',0:2:max(max(x)),'YTick',0:2:max(max(y)));
    addPoints();
    addDescription();

    figure('Position',[100 50 1000 530]);
    axes('Position',[0.06,0.1,0.90,0.83]);
    contour(x, y, map);
    set(gca,'XTick',0:2:max(max(x)),'YTick',0:2:max(max(y)));
    grid
    colormap(jet);
    axis equal;
    hold on;
    addPoints();
    addDescription();
end

function [map,xg,yg] = readDTMv1(filename)
    d = importdata(filename);
    x = d.data(:,1);
    y = d.data(:,2);
    h = d.data(:,3);

    dx = unique(x); dx = dx(2)-dx(1);
    dy = unique(y); dy = dy(2)-dy(1);
    mxX = max(x);
    mxY = max(y);
    mnX = min(x);
    mnY = min(y);
    [xg,yg] = meshgrid(mnX:dx:mxX, mnY:dy:mxY);
    map = griddata(x,y,h,xg,yg,'nearest');
end

function [map,xg,yg] = readDTMv2(filename)
    d = importdata(filename);
    map = flipud(d.data);
    q = str2num(d.textdata{2});
    dx = q(3);
    dy = q(4);
    mnX = q(5);
    mxX = mnX + dx*(q(2)-1);
    mxY = q(6);
    mnY = mxY - dy*(q(1)-1);
    [xg,yg] = meshgrid(mnX:dx:mxX, mnY:dy:mxY);
end

function addPoints
    d = importdata('Landmarks.txt');
    n = d.textdata(2:end,1);
    x = d.data(:,1);
    y = d.data(:,2);
    c = [0 0.7 0];
    plot(x,y,'.','Color',c,'MarkerSize',25);
    text(x,y+1,n,'Horizontalalignment','center');

    d = importdata('Waypoints.txt');
    n = d.textdata(2:end,1);
    x = d.data(:,1);
    y = d.data(:,2);
    plot(x,y,'r.','MarkerSize',25);
    text(x,y+1,n,'Horizontalalignment','center');

    d = importdata('AuxPoints.txt');
    n = d.textdata(2:end,1);
    x = d.data(:,1);
    y = d.data(:,2);
    r = d.data(:,3);
    plot(x,y,'k.','MarkerSize',25);
    text(x,y+1,n,'Horizontalalignment','center');
    a=-pi:pi/10:pi;
    xc = sin(a);
    yc = cos(a);
    for i=1:length(r)
        plot(x(i)+r(i)*xc, y(i)+r(i)*yc,'k');
    end

    d = importdata('StartArea.txt');
    n = d.textdata(2:end,1);
    x = d.data(:,1);
    y = d.data(:,2);
    r = d.data(:,3);
    plot(x,y,'b.','MarkerSize',25);
    text(x,y+1,n,'Horizontalalignment','center');
    for i=1:length(r)
        plot(x(i)+r(i)*xc, y(i)+r(i)*yc,'b');
    end

%-----------------------------------------------
%     d = importdata('erc.txt');
%     x = d(:,2);
%     y = -d(:,3);
%     plot(x,y,'k.','MarkerSize',25);
%-----------------------------------------------
    
    
end

function addDescription
    hc = colorbar;
    xlabel('[m]');
    ylabel('[m]');
    title({'ERC 2018 - traversal task',''});
    title(hc,'height [m]');
end
